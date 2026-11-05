"""Prepare actual narration, cache by request, and compile one shared timeline."""
import asyncio
import hashlib
import json
import subprocess
import wave
from pathlib import Path

import numpy as np
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

from timeline_tools import build_timeline, checked_id

ROOT = Path(__file__).resolve().parent
SR = 48000


def probe(path):
    return float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(path)
    ], text=True))


def prepare_font():
    source = ROOT / "assets/fonts/NotoSansSC.ttf"
    target = source.with_name("NotoSansSC-Medium.ttf")
    signature = hashlib.sha256(source.read_bytes() + b"weight=600").hexdigest()
    stamp = source.with_name("prepared.json")
    if target.exists() and stamp.exists() and json.loads(stamp.read_text()).get("source") == signature:
        return
    font = TTFont(source)
    instantiateVariableFont(font, {"wght": 600}, inplace=True)
    font.save(target)
    stamp.write_text(json.dumps({"source": signature, "weight": 600}, indent=2))


def read_words(path):
    result = []
    for line in Path(path).read_text().splitlines():
        item = json.loads(line)
        if item.get("type") == "WordBoundary":
            result.append({"text": item["text"], "start": item["offset"] / 10_000_000,
                           "end": (item["offset"] + item["duration"]) / 10_000_000})
    return result


async def narration(project):
    options = project.get("narration", {})
    recordings = {}
    for segment in project["segments"]:
        name = checked_id(segment["id"])
        provider = segment.get("provider", options.get("provider", "none"))
        if provider == "none":
            recordings[name] = {"provider": "none", "duration": 0, "words": []}
            continue
        request = {"provider": provider, "text": segment.get("text", ""),
                   "voice": options.get("voice", "zh-CN-YunxiNeural"),
                   "rate": options.get("rate", "+0%")}
        if provider == "file":
            source = (ROOT / segment["audio_file"]).resolve()
            request["file_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
        key = hashlib.sha256(json.dumps(request, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]
        prefix = ROOT / "audio" / f"{name}-{key}"
        words = []
        if provider == "edge":
            import edge_tts
            audio = prefix.with_suffix(".mp3")
            metadata = prefix.with_suffix(".jsonl")
            ready = audio.exists() and audio.stat().st_size > 0 and metadata.exists() and metadata.stat().st_size > 0
            if not ready:
                try:
                    await edge_tts.Communicate(
                        request["text"], request["voice"], rate=request["rate"],
                        boundary="WordBoundary"
                    ).save(str(audio), str(metadata))
                except Exception as error:
                    prefix.with_suffix(".failure.json").write_text(json.dumps({
                        "provider": "edge", "status": "failed", "error_type": type(error).__name__,
                        "reason": str(error), "cached_files_preserved": True
                    }, ensure_ascii=False, indent=2))
                    raise RuntimeError("TTS request failed; cached files were preserved. Check the network/service, or explicitly use an existing audio_file. No silent narration fallback was applied.") from error
            words = read_words(metadata)
        elif provider == "file":
            audio = source
            if segment.get("timing_file"):
                words = read_words((ROOT / segment["timing_file"]).resolve())
        else:
            raise ValueError(f"Unsupported narration provider: {provider}")
        wav = prefix.with_suffix(".wav")
        if not wav.exists():
            subprocess.run(["ffmpeg", "-v", "error", "-i", str(audio), "-ac", "1",
                            "-ar", str(SR), "-c:a", "pcm" + "_s16le", "-y", str(wav)], check=True)
        failure = prefix.with_suffix(".failure.json")
        if failure.exists():
            failure.unlink()
        prefix.with_suffix(".request.json").write_text(json.dumps(request, ensure_ascii=False, indent=2))
        recordings[name] = {"provider": provider, "duration": probe(wav),
                            "audio_path": str(wav.relative_to(ROOT)), "words": words}
    return recordings


def write_voice(timeline):
    data = np.zeros(round(timeline["duration"] * SR), dtype=np.float32)
    for segment in timeline["segments"]:
        if not segment.get("audio_path"):
            continue
        with wave.open(str(ROOT / segment["audio_path"])) as f:
            x = np.frombuffer(f.readframes(f.getnframes()), "<i2").astype(np.float32) / 32768
        start = round(segment["voice_start"] * SR)
        data[start:start + len(x)] += x
    with wave.open(str(ROOT / "audio/narration.wav"), "wb") as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes((np.column_stack([data, data]).clip(-.98, .98) * 32767).astype("<i2").tobytes())


async def main():
    for name in ["audio", "qa", "render", "out"]:
        (ROOT / name).mkdir(exist_ok=True)
    project = json.loads((ROOT / "project.json").read_text())
    records = await narration(project)
    timeline = build_timeline(project, records)
    prepare_font()
    (ROOT / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=2))
    write_voice(timeline)
    print(json.dumps({"duration": timeline["duration"], "frames": timeline["frames"],
                      "segments": len(timeline["segments"]), "shots": len(timeline["shots"]),
                      "events": len(timeline["events"])}, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
