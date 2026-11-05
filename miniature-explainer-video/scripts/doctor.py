#!/usr/bin/env python3
"""Read-only tool inventory; report every candidate rather than assuming PATH."""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path


def candidates(name, flag):
    found = []
    seen = set()
    for directory in os.get_exec_path():
        path = Path(directory) / name
        if str(path) in seen or not path.is_file() or not os.access(path, os.X_OK):
            continue
        seen.add(str(path))
        try:
            result = subprocess.run([str(path), flag], capture_output=True, text=True, timeout=20)
            lines = (result.stdout + result.stderr).splitlines()
            version = next((s for s in lines if s.strip()), "")
        except (OSError, subprocess.TimeoutExpired) as error:
            version = type(error).__name__
        found.append({"path": str(path), "realpath": str(path.resolve()), "version": version})
    return found


def main():
    tools = {name: candidates(name, flag) for name, flag in [
        ("blender", "--version"), ("ffmpeg", "-version"), ("ffprobe", "-version"),
        ("uv", "--version")
    ]}
    modules = {name: importlib.util.find_spec(name) is not None for name in [
        "PIL", "numpy", "scipy", "fontTools", "edge_tts"
    ]}
    result = {"python": sys.executable, "tools": tools, "python_modules": modules,
              "missing_system_tools": [n for n in ["blender", "ffmpeg", "ffprobe"] if not tools[n]]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["missing_system_tools"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
