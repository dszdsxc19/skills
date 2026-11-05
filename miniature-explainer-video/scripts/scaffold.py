#!/usr/bin/env python3
"""Copy the runnable, explicitly labelled example into a fresh project directory."""
import argparse
import json
import shutil
from pathlib import Path


def create(destination):
    skill = Path(__file__).resolve().parents[1]
    destination = Path(destination).expanduser().resolve()
    if destination.exists() and any(destination.iterdir()):
        raise ValueError(f"Project directory is not empty: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copytree(skill / "assets/project", destination, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copytree(skill / "assets/fonts", destination / "assets/fonts", dirs_exist_ok=True)
    shutil.copytree(skill / "assets/piano", destination / "assets/piano", dirs_exist_ok=True)
    shutil.copy2(skill / "assets/credits.json", destination / "assets/credits.json")
    for name in ["audio", "render", "qa", "out"]:
        (destination / name).mkdir(exist_ok=True)
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project")
    args = parser.parse_args()
    try:
        path = create(args.project)
    except (ValueError, OSError) as error:
        parser.exit(2, str(error) + "\n")
    print(json.dumps({"project": str(path), "example": "6-second package sorting",
                      "next": "Edit project.json, scene.py, compose.py and score.py for the actual film."},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
