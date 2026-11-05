"""Versioned per-shot frames, explicit manifest, interruption-safe cache reuse."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parent


def complete_png(path):
    try:
        with path.open("rb") as f:
            if f.read(8) != b"\x89PNG\r\n\x1a\n":
                return False
            f.seek(-12, 2)
            return f.read(12) == b"\x00\x00\x00\x00IEND\xaeB`\x82"
    except (OSError, ValueError):
        return False


def render_shots(only=None, stills=False):
    film = json.loads((ROOT / "timeline.json").read_text())
    project = ROOT / "scene.blend"
    blend_sha = hashlib.sha256(project.read_bytes()).hexdigest()
    spec = {k: film[k] for k in ["width", "height", "fps", "frames"]}
    record = ROOT / ("qa/preview_manifest.json" if stills else "render/manifest.json")
    manifest = json.loads(record.read_text()) if record.exists() else {"shots": {}}
    manifest["spec"] = spec
    manifest["frame_index"] = "zero-based, end-exclusive"
    scene = bpy.context.scene
    if (scene.render.resolution_x, scene.render.resolution_y, scene.render.fps) != (film["width"], film["height"], film["fps"]):
        raise ValueError("Blender project and timeline use different output specifications; rebuild scene.blend.")
    scene.render.resolution_percentage = 100
    known = {s["id"] for s in film["shots"]}
    if only and set(only) - known:
        raise ValueError(f"Unknown shots: {sorted(set(only)-known)}")
    for shot in film["shots"]:
        if only and shot["id"] not in only:
            continue
        entry = {k: shot[k] for k in ["id", "start_frame", "end_frame"]}
        entry["spec"] = {k: spec[k] for k in ["width", "height", "fps"]}
        entry["mode"] = shot.get("mode", "3d")
        entry["blend_sha256"] = blend_sha
        key = hashlib.sha256(json.dumps({"entry": entry, "spec": spec}, sort_keys=True).encode()).hexdigest()[:16]
        folder = ROOT / ("qa/stills" if stills else "render") / f"{shot['id']}-{key}"
        folder.mkdir(parents=True, exist_ok=True)
        entry["directory"] = str(folder.relative_to(ROOT))
        entry["frame_indices"] = []
        if entry["mode"] == "3d":
            frames = range(shot["start_frame"], shot["end_frame"])
            if stills:
                frames = sorted({shot["start_frame"], (shot["start_frame"] + shot["end_frame"]) // 2, shot["end_frame"] - 1})
            for frame in frames:
                target = folder / f"frame-{frame:06}.png"
                if not complete_png(target):
                    scene.frame_set(frame + 1)
                    scene.render.filepath = str(target)
                    bpy.ops.render.render(write_still=True)
                entry["frame_indices"].append(frame)
        entry["complete"] = True
        manifest["shots"][shot["id"]] = entry
        record.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
        print("SHOT_READY", shot["id"], len(entry["frame_indices"]), "frames", flush=True)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--shots", help="Comma-separated shot IDs")
    parser.add_argument("--stills", action="store_true")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    render_shots(args.shots.split(",") if args.shots else None, args.stills)
