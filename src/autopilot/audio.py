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


# Moods: the same soft pad, with a different colour (never a beat, never a tune that competes with the voice).
MOODS = {
    "curious": {"progressions": [[(0, 4, 7, 11), (5, 9, 12, 16), (7, 11, 14, 17), (2, 5, 9, 12)],
                                 [(0, 4, 7, 14), (9, 12, 16, 19), (5, 9, 12, 16), (7, 11, 14, 19)]],
                "bells": 0.16, "bell_every": (2.0, 4.5), "drone": 0.0},
    "mysterious": {"progressions": [[(0, 3, 6, 9), (1, 4, 8, 11), (0, 3, 7, 10), (-2, 1, 5, 8)],
                                    [(0, 3, 7, 10), (1, 5, 8, 12), (0, 3, 6, 10), (-1, 3, 6, 9)]],
                   "bells": 0.10, "bell_every": (5.0, 9.0), "drone": 0.55},
}


# Brightwork topic categories -> mood (jobs from before the topic mix have no category and count as "core").
MOOD_BY_CATEGORY = {"space": "mysterious", "what_if": "mysterious", "core": "curious", "history": "plain"}
# Plotline data themes (config/plotline_catalog.yaml) -> mood: stakes and money feel mysterious, everyday life curious.
MOOD_BY_THEME = {"housing": "mysterious", "money": "mysterious", "inflation": "mysterious", "energy": "mysterious", "planet": "mysterious",
                 "health": "mysterious", "food": "curious", "jobs": "curious", "pay": "curious", "people": "curious", "shopping": "curious",
                 "tech": "curious", "cars": "curious", "uk": "plain"}


def mood_for_category(category: str | None) -> str:
    return MOOD_BY_CATEGORY.get(category or "core", "curious")


def mood_for_theme(theme: str | None) -> str:
    return MOOD_BY_THEME.get(theme or "", "plain")


def _bell(freq: float, seconds: float = 3.2) -> np.ndarray:
    """A soft struck-bell note: a few partials that die away."""
    t = np.arange(int(seconds * RATE)) / RATE
    tone = np.sin(2 * np.pi * freq * t) + 0.4 * np.sin(2 * np.pi * freq * 2.76 * t) + 0.2 * np.sin(2 * np.pi * freq * 5.4 * t)
    return tone * np.exp(-t * 1.6) * np.minimum(1.0, t * 60)


def generate_ambient(seconds: float, out_wav: Path, seed: int = 0, mood: str = "plain") -> Path:
    rng = np.random.default_rng(seed)
    root = 55.0 * 2 ** (rng.integers(0, 12) / 12)  # A1 .. G#2 region
    cfg = MOODS.get(mood)
    progression = cfg["progressions"][seed % len(cfg["progressions"])] if cfg else PROGRESSIONS[seed % len(PROGRESSIONS)]
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
    if cfg:                                   # a mood adds colour on top of the pad; the pad itself is made exactly as before
        mood_rng = np.random.default_rng(seed + 7)
        if cfg["drone"]:                      # a deep, slowly breathing note under everything
            drone = np.sin(2 * np.pi * root * 0.5 * t) + 0.5 * np.sin(2 * np.pi * root * 0.5 * 1.004 * t)
            mix += cfg["drone"] * drone * (0.7 + 0.3 * np.sin(2 * np.pi * 0.07 * t)) / 1.5
        pos = 3.0
        while pos < seconds - 1.0:            # sparse bell notes from the current chord, high up
            chord = progression[int(pos // CHORD_SECONDS) % len(progression)]
            note = root * 2 ** ((chord[int(mood_rng.integers(0, len(chord)))] + 36) / 12)
            bell = _bell(note) * cfg["bells"]
            start = int(pos * RATE)
            end = min(n, start + len(bell))
            mix[start:end] += bell[: end - start]
            pos += float(mood_rng.uniform(*cfg["bell_every"]))
        mix /= max(1e-9, np.abs(mix).max())
    mix *= 0.8
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes((mix * 32767).astype("<i2").tobytes())
    return out_wav
