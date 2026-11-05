"""Short demonstration arrangement; rewrite its musical arc for the current story."""
import json
from pathlib import Path

import numpy as np

from audio_tools import SR, add, piano, bass, brush, tick, finish

ROOT = Path(__file__).resolve().parent


def main():
    film = json.loads((ROOT/"timeline.json").read_text())
    n = round(film["duration"]*SR)
    music = np.zeros((n, 2), np.float32); effects = np.zeros_like(music)
    if film.get("audio", {}).get("music", True):
        beat = 60/108
        chords = [[50, 57, 60, 64], [46, 53, 57, 60], [53, 57, 60, 65], [48, 55, 60, 64]]
        for bar, onset in enumerate(np.arange(0, film["duration"]-.25, 4*beat)):
            chord = chords[bar % len(chords)]
            for i, index in enumerate([0, 2, 1, 3, 2, 1, 3, 2]):
                add(music, piano(chord[index]+(12 if i == 7 else 0), 1.3),
                    onset+i*.5*beat, .058, (index-1.5)*.2)
            for i in [0, 2]:
                add(music, bass(chord[0]-12, .9), onset+i*beat, .040, -.1)
            for i in [1, 3]:
                add(music, brush(.25, bar*5+i), onset+i*beat, .022, .25)
    if film.get("audio", {}).get("effects", True):
        for index, event in enumerate(film["events"]):
            add(effects, tick(.20, 1250+index*140), event["time"], .045, -.4+index*.25)
    credits = finish(film, music, effects)
    print("AUDIO_READY", film["duration"], "seconds", len(film["events"]), "action cues", credits["audio_enabled"])


if __name__ == "__main__":
    main()
