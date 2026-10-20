"""Procedural ambient music bed. Generated from scratch, so there is no licence or Content ID risk."""
import wave
from pathlib import Path

import numpy as np

RATE = 44100
# Slow minor-ish progressions as semitone offsets from the root; each chord lasts CHORD_SECONDS.
PROGRESSIONS = [
    [(0, 3, 7, 10), (8, 12, 15, 19), (5, 8, 12, 15), (10, 14, 17, 21)],
    [(0, 7, 10, 14), (3, 7, 10, 14), (5, 9, 12, 16), (7, 10, 14, 17)],
    [(0, 3, 7, 12), (-2, 2, 5, 9), (-4, 0, 3, 7), (-5, 2, 7, 10)],
]
CHORD_SECONDS = 12.0


def _pad(freq: float, t: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Soft pad voice: a few detuned sines with slow tremolo."""
    out = np.zeros_like(t)
    for detune in (-0.12, 0.0, 0.1):
        phase = rng.uniform(0, 2 * np.pi)
        out += np.sin(2 * np.pi * freq * (1 + detune / 100) * t + phase)
        out += 0.3 * np.sin(2 * np.pi * freq * 2 * (1 + detune / 100) * t + phase)
    lfo = 0.75 + 0.25 * np.sin(2 * np.pi * rng.uniform(0.05, 0.15) * t + rng.uniform(0, 6.28))
    return out * lfo / 6


def generate_ambient(seconds: float, out_wav: Path, seed: int = 0) -> Path:
    rng = np.random.default_rng(seed)
    root = 55.0 * 2 ** (rng.integers(0, 12) / 12)  # A1 .. G#2 region
    progression = PROGRESSIONS[seed % len(PROGRESSIONS)]
    n = int(seconds * RATE)
    t = np.arange(n) / RATE
    mix = np.zeros(n)
    chord_len = int(CHORD_SECONDS * RATE)
    fade = int(3.0 * RATE)  # long crossfade between chords
    for i, start in enumerate(range(0, n, chord_len)):
        chord = progression[i % len(progression)]
        end = min(n, start + chord_len + fade)
        tt = t[start:end]
        seg = sum(_pad(root * 2 ** ((st + 12) / 12), tt, rng) for st in chord)
        env = np.ones(end - start)
        ramp = min(fade, end - start)
        env[:ramp] = np.linspace(0, 1, ramp)
        env[-ramp:] = np.minimum(env[-ramp:], np.linspace(1, 0, ramp))
        mix[start:end] += seg * env
    mix /= max(1e-9, np.abs(mix).max())
    mix *= 0.8
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes((mix * 32767).astype("<i2").tobytes())
    return out_wav
