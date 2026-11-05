"""Sampling and stereo mixing primitives. Arrangement remains in score.py."""
import json
import math
import subprocess
import wave
from functools import lru_cache
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt

ROOT = Path(__file__).resolve().parent
SR = 48000
SAMPLE_MIDI = {"C2": 36, "C3": 48, "Fs3": 54, "C4": 60, "Ds4": 63,
               "Fs4": 66, "A4": 69, "C5": 72, "Fs5": 78}
USED = set()


def write_wave(path, x):
    if x.ndim == 1:
        x = np.column_stack([x, x])
    with wave.open(str(path), "wb") as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes((np.clip(x, -.98, .98) * 32767).astype("<i2").tobytes())


def read_wave(path):
    with wave.open(str(path)) as f:
        return np.frombuffer(f.readframes(f.getnframes()), "<i2").astype(np.float32).reshape(-1, f.getnchannels()) / 32768


def add(bus, data, onset, gain=1, pan=0):
    start = round(onset * SR)
    if start < 0:
        data = data[-start:]; start = 0
    end = min(len(bus), start + len(data))
    if end <= start:
        return
    data = data[:end-start]
    if data.ndim == 1:
        bus[start:end, 0] += data * gain * math.cos((pan+1)*math.pi/4)
        bus[start:end, 1] += data * gain * math.sin((pan+1)*math.pi/4)
    else:
        bus[start:end] += data * gain * np.array([1-max(pan, 0)*.5, 1+min(pan, 0)*.5])


@lru_cache(maxsize=12)
def sample(name):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(ROOT/f"assets/piano/{name}.mp3"),
                                   "-ar", str(SR), "-ac", "2", "-f", "f32le", "pipe:1"])
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    x /= max(.15, float(np.max(np.abs(x))))
    return x


@lru_cache(maxsize=96)
def piano(midi, seconds):
    name = min(SAMPLE_MIDI, key=lambda n: abs(SAMPLE_MIDI[n]-midi))
    USED.add(name + ".mp3")
    source = sample(name)
    t = np.arange(round(seconds*SR))/SR
    pos = np.arange(len(t)) * 2**((midi-SAMPLE_MIDI[name])/12)
    x = np.column_stack([np.interp(pos, np.arange(len(source)), source[:, ch], right=0) for ch in range(2)])
    env = np.minimum(t/.006, 1) * np.clip((seconds-t)/.15, 0, 1)
    return (x * env[:, None]).astype(np.float32)


def bass(midi, seconds):
    t = np.arange(round(seconds*SR))/SR
    frequency = 440*2**((midi-69)/12)
    env = np.minimum(t/.008, 1)*np.exp(-t*2)*np.clip((seconds-t)/.08, 0, 1)
    return (np.sin(t*math.tau*frequency)+.2*np.sin(t*math.tau*frequency*2))*env


def brush(seconds, seed=0):
    t = np.arange(round(seconds*SR))/SR
    noise = np.random.default_rng(seed).normal(size=len(t))
    x = sosfilt(butter(2, [1400, 6500], fs=SR, btype="bandpass", output="sos"), noise)
    return x*np.exp(-t*25)


def tick(seconds=.20, frequency=1500):
    t = np.arange(round(seconds*SR))/SR
    return (np.sin(t*math.tau*frequency)+.25*np.sin(t*math.tau*frequency*1.73))*np.exp(-t*38)


def finish(film, music, effects):
    duration = film["duration"]
    voice = read_wave(ROOT/"audio/narration.wav")
    count = round(duration*SR)
    duck = np.ones(count)
    for segment in film["segments"]:
        if segment.get("audio_path"):
            start = round(segment["voice_start"]*SR)
            end = min(count, round((segment["voice_start"]+segment["voice_duration"])*SR))
            duck[start:end] = .65
    duck = sosfilt(butter(1, 5, fs=SR, output="sos"), duck)
    wet = np.zeros_like(music)
    for seconds, gain in [(.043, .12), (.079, .09), (.139, .06)]:
        offset = round(seconds*SR)
        if offset < count:
            wet[offset:] += music[:-offset, ::-1]*gain
    time = np.arange(count)/SR
    fade = np.minimum(time/.15, 1)*np.clip((duration-time)/.35, 0, 1)
    music = (music+wet)*duck[:, None]*fade[:, None]
    effects = effects*fade[:, None]
    mixed = voice*.83 + music + effects
    for name, data in [("music", music), ("effects", effects), ("mix-raw", mixed)]:
        write_wave(ROOT/f"audio/{name}.wav", data)
    audio_on = bool(USED or np.max(np.abs(effects)) > 0 or any(s.get("audio_path") for s in film["segments"]))
    if audio_on:
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(ROOT/"audio/mix-raw.wav"),
                        "-af", "loudnorm=I=-16:TP=-1.8:LRA=7", "-ar", str(SR),
                        "-c:a", "pcm"+"_s16le", "-y", str(ROOT/"audio/final.wav")], check=True)
    else:
        write_wave(ROOT/"audio/final.wav", mixed)
    catalog = json.loads((ROOT/"assets/credits.json").read_text())
    credits = {"piano_samples": sorted(USED), "fonts": catalog["fonts"], "audio_enabled": audio_on}
    if USED:
        for key in ["piano", "license", "license_url", "source", "changes"]:
            credits[key] = catalog[key]
    (ROOT/"audio/credits.json").write_text(json.dumps(credits, ensure_ascii=False, indent=2))
    return credits
