"""Pure timing rules shared by narration, animation, sound and composition."""
import math
import re
import unicodedata


def normalized(text):
    return "".join(c for c in text if unicodedata.category(c)[0] not in "PZ")


def checked_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", value):
        raise ValueError(f"Unsafe or unsupported identifier: {value!r}")
    return value


def locate_words(words, anchors):
    joined = ""
    spans = []
    for word in words:
        token = normalized(word["text"])
        spans.append((len(joined), len(joined) + len(token), word))
        joined += token
    result = {}
    for name, specification in anchors.items():
        text = specification if isinstance(specification, str) else specification["text"]
        occurrence = 1 if isinstance(specification, str) else specification.get("occurrence", 1)
        if occurrence < 1 or not normalized(text):
            raise ValueError(f"Invalid anchor: {name}")
        cursor = 0
        for _ in range(occurrence):
            pos = joined.find(normalized(text), cursor)
            if pos < 0:
                raise ValueError(f"Anchor not present in actual word timings: {name} / {text}")
            cursor = pos + len(normalized(text))
        word = next(w for a, b, w in spans if a <= pos < b)
        result[name] = {"time": word["start"], "precision": "word",
                        "text": text, "occurrence": occurrence}
    return result


def sentence_captions(text, words):
    joined = ""
    spans = []
    for word in words:
        token = normalized(word["text"])
        spans.append((len(joined), len(joined) + len(token), word))
        joined += token
    captions = []
    cursor = 0
    for sentence in filter(None, re.split(r"(?<=[。！？!?])", text)):
        target = normalized(sentence)
        pos = joined.find(target, cursor)
        if not target:
            continue
        if pos < 0:
            raise ValueError(f"Caption text not found in word timings: {sentence}")
        selected = [w for a, b, w in spans if b > pos and a < pos + len(target)]
        captions.append({"text": sentence, "start": selected[0]["start"],
                         "end": selected[-1]["end"], "precision": "word"})
        cursor = pos + len(target)
    return captions


def frame_boundary(value, fps):
    frame = round(value * fps)
    if abs(value * fps - frame) > 1e-5:
        raise ValueError(f"Shot boundary {value}s is not on the {fps}fps grid; use {frame/fps:.8f}s.")
    return frame


def build_timeline(project, recordings):
    width, height, fps = project["width"], project["height"], project["fps"]
    if any(not isinstance(v, int) or v <= 0 for v in (width, height, fps)):
        raise ValueError("Width, height and fps must be positive integers.")
    if width % 2 or height % 2:
        raise ValueError("The default yuv420p export needs even width and height.")
    output = project.get("output_name", "final.mp4")
    if "/" in output or "\\" in output or not output.endswith(".mp4"):
        raise ValueError("output_name must be a local .mp4 basename.")
    options = project.get("narration", {})
    segments, cues, cursor = [], {}, 0.0
    seen_segments = set()
    for source in project["segments"]:
        name = checked_id(source["id"])
        if name in seen_segments:
            raise ValueError(f"Duplicate segment: {name}")
        seen_segments.add(name)
        record = recordings[name]
        provider = record["provider"]
        lead = float(options.get("lead", .2)) if provider != "none" else 0
        tail = float(options.get("tail", .4)) if provider != "none" else 0
        required = lead + record["duration"] + tail
        requested = source.get("duration")
        if requested is None and provider == "none":
            raise ValueError(f"Manual segment needs a duration: {name}")
        if requested is not None and (requested <= 0 or required > requested + 1e-6):
            raise ValueError(f"Audio needs {required:.3f}s but segment {name} allows {requested}s; keep audio and revise the plan.")
        duration = math.ceil(float(requested if requested is not None else required) * fps - 1e-7) / fps
        voice_start = cursor + lead
        words = [{**w, "start": voice_start + w["start"], "end": voice_start + w["end"]}
                 for w in record.get("words", [])]
        segment = {**source, "provider": provider, "start": cursor, "end": cursor + duration,
                   "duration": duration, "voice_start": voice_start,
                   "voice_duration": record["duration"], "audio_path": record.get("audio_path"),
                   "words": words, "precision": "word" if words else ("manual" if provider == "none" else "segment")}
        if words:
            for key, cue in locate_words(words, source.get("anchors", {})).items():
                cues[f"{name}.{checked_id(key)}"] = cue
            segment["captions"] = sentence_captions(source.get("text", ""), words)
        else:
            if source.get("anchors") and provider != "none":
                missing = set(source["anchors"]) - set(source.get("manual_cues", {}))
                if missing:
                    raise ValueError(f"No word timings for {name}; supply verified manual_cues for {sorted(missing)} or use segment timing.")
            segment["captions"] = ([{"text": source["text"], "start": voice_start,
                                     "end": voice_start + record["duration"], "precision": "segment"}]
                                   if provider != "none" and source.get("text") else [])
        for key, at in source.get("manual_cues", {}).items():
            if not 0 <= float(at) < duration:
                raise ValueError(f"Manual cue outside segment: {name}.{key}")
            cues[f"{name}.{checked_id(key)}"] = {"time": cursor + float(at), "precision": "manual"}
        segments.append(segment)
        cursor += duration
    by_id = {s["id"]: s for s in segments}
    shots, events, seen_shots, seen_events = [], [], set(), set()
    for source in project["shots"]:
        name = checked_id(source["id"])
        if name in seen_shots:
            raise ValueError(f"Duplicate shot: {name}")
        seen_shots.add(name)
        segment = by_id[source["segment"]]
        start = segment["start"] + float(source.get("in", 0))
        relative_end = source.get("out", "end")
        end = segment["end"] if relative_end == "end" else segment["start"] + float(relative_end)
        if not segment["start"] <= start < end <= segment["end"] + 1e-6:
            raise ValueError(f"Invalid shot range: {name}")
        shot = {**source, "start": start, "end": end,
                "start_frame": frame_boundary(start, fps), "end_frame": frame_boundary(end, fps)}
        shots.append(shot)
        for source_event in source.get("beats", []):
            event_id = checked_id(source_event["id"])
            if event_id in seen_events:
                raise ValueError(f"Duplicate event: {event_id}")
            seen_events.add(event_id)
            if "cue" in source_event:
                cue = cues[source_event["cue"]]
                at, precision = cue["time"], cue["precision"]
            else:
                at, precision = start + float(source_event["at"]), "manual"
            if not start <= at < end:
                raise ValueError(f"Event outside its shot: {event_id}")
            duration = float(source_event.get("duration", 0))
            if duration < 0 or at + duration > cursor + 1e-6:
                raise ValueError(f"Event result falls outside the film: {event_id}")
            events.append({**source_event, "id": event_id, "shot": name,
                           "time": at, "duration": duration, "precision": precision})
    shots.sort(key=lambda s: s["start_frame"])
    expected = 0
    for shot in shots:
        if shot["start_frame"] != expected:
            raise ValueError(f"Timeline gap or overlap before shot: {shot['id']}")
        if shot.get("mode", "3d") not in ("3d", "graphic"):
            raise ValueError(f"Unknown shot mode: {shot['id']}")
        expected = shot["end_frame"]
    if expected != round(cursor * fps):
        raise ValueError("Shots must cover the complete narration timeline.")
    return {**project, "segments": segments, "shots": shots, "cues": cues,
            "events": sorted(events, key=lambda e: e["time"]), "duration": cursor,
            "frames": expected, "frame_index": "zero-based, end-exclusive"}
