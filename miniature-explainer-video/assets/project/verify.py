"""Check final media facts; keep aesthetic and heuristic observations separate."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent


def run(args):
    return subprocess.run(args, check=True, capture_output=True)


def main():
    film = json.loads((ROOT/"timeline.json").read_text())
    movie = ROOT/"out"/film.get("output_name", "final.mp4")
    credits = json.loads((ROOT/"audio/credits.json").read_text())
    probe = json.loads(run(["ffprobe", "-v", "error", "-count_frames", "-show_streams",
                            "-show_format", "-of", "json", str(movie)]).stdout)
    video = next(s for s in probe["streams"] if s["codec_type"] == "video")
    audio = next((s for s in probe["streams"] if s["codec_type"] == "audio"), None)
    checks = {
        "dimensions": (video["width"], video["height"]) == (film["width"], film["height"]),
        "fps": video["avg_frame_rate"] == f"{film['fps']}/1",
        "frame_count": int(video["nb_read_frames"]) == film["frames"],
        "duration": abs(float(probe["format"]["duration"])-film["duration"]) < 1/film["fps"]+.02,
        "audio_presence": bool(audio) == credits["audio_enabled"],
        "continuous_shots": film["shots"][0]["start_frame"] == 0
            and film["shots"][-1]["end_frame"] == film["frames"]
            and all(a["end_frame"] == b["start_frame"] for a, b in zip(film["shots"], film["shots"][1:]))
    }
    command = ["ffmpeg", "-hide_banner", "-v", "info", "-i", str(movie),
               "-vf", "blackdetect=d=.20:pix_th=.04"]
    if audio:
        checks["audio_duration"] = abs(float(audio["duration"])-film["duration"]) < .12
        command += ["-af", "loudnorm=I=-16:TP=-1.8:LRA=7:print_format=json"]
    decode = run(command+["-f", "null", "-"]).stderr.decode()
    checks["full_decode"] = True
    observations = {
        "black_intervals": re.findall(r"black_start:[^\n]+", decode),
        "audio_levels": None,
        "note": "Black intervals, loudness and stereo width are observations, not universal aesthetic gates."
    }
    if audio:
        match = re.findall(r'\{\s*"input_i"[\s\S]+?\}', decode)
        observations["audio_levels"] = json.loads(match[-1]) if match else None
        raw = run(["ffmpeg", "-v", "error", "-i", str(movie), "-vn", "-ar", "16000",
                   "-ac", "2", "-f", "f32le", "pipe:1"]).stdout
        x = np.frombuffer(raw, np.float32).reshape(-1, 2)
        mid = x.mean(axis=1); side = (x[:, 0]-x[:, 1])/2
        observations["stereo_side_energy_fraction"] = float(np.mean(side**2)/(np.mean(mid**2)+np.mean(side**2)+1e-20))
    if credits.get("piano_samples"):
        checks["sample_attribution"] = all(credits.get(k) for k in ["piano", "license", "source", "changes"])
    report = {
        "movie": movie.name, "checks": checks, "observations": observations,
        "duration": float(probe["format"]["duration"]), "frames": int(video["nb_read_frames"]),
        "segments": len(film["segments"]), "shots": len(film["shots"]),
        "events": len(film["events"]), "bytes": movie.stat().st_size,
        "sha256": hashlib.sha256(movie.read_bytes()).hexdigest()
    }
    (ROOT/"qa/verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    (ROOT/"qa/decode.log").write_text(decode)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
