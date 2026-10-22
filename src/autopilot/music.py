"""Beat-driven background music, synthesized from scratch (no samples, so no licence or Content ID risk).

Drums, a bass that pumps with the kick, plucked arpeggios and risers, in a few styles. Pure numpy."""
import wave
from pathlib import Path

import numpy as np

RATE = 44100

# chord = (semitones above the key root, triad type). A minor-ish progression with some lift.
PROGRESSIONS = [
    [(0, "m"), (8, "M"), (3, "M"), (10, "M")],   # i  VI  III  VII
    [(0, "m"), (5, "m"), (8, "M"), (7, "M")],    # i  iv  VI   V
    [(0, "m"), (3, "M"), (10, "M"), (8, "M")],   # i  III VII  VI
]
TRIAD = {"m": (0, 3, 7), "M": (0, 4, 7)}

# 16 steps per bar. 1 = hit. swing delays every second 16th by that fraction of a step.
STYLES = {
    "upbeat": {"bpm": 112, "kick": [1,0,0,0, 1,0,0,0, 1,0,0,0, 1,0,0,0], "snare": [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
                   "hat": [0,0,1,0]*4, "arp": [1,0,1,1, 0,1,1,0, 1,0,1,1, 0,1,1,0], "swing": 0.0, "arp_gain": 0.30, "bass_gain": 0.55},
    "lofi": {"bpm": 84, "kick": [1,0,0,0, 0,0,1,0, 0,0,1,0, 0,0,0,0], "snare": [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
                 "hat": [1,0,1,0]*4, "arp": [1,0,0,1, 0,0,1,0, 0,1,0,0, 1,0,0,0], "swing": 0.28, "arp_gain": 0.34, "bass_gain": 0.5},
    "pulse": {"bpm": 100, "kick": [1,0,0,1, 0,0,1,0, 1,0,0,1, 0,0,1,0], "snare": [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,1],
                  "hat": [1,1,1,1]*4, "arp": [1,1,1,1]*4, "swing": 0.0, "arp_gain": 0.22, "bass_gain": 0.6},
}


def _noise(n: int, rng: np.random.Generator) -> np.ndarray:
    return rng.uniform(-1, 1, n)


def _kick() -> np.ndarray:
    t = np.arange(int(0.32 * RATE)) / RATE
    phase = 2 * np.pi * np.cumsum(46 + 110 * np.exp(-t * 30)) / RATE
    return np.sin(phase) * np.exp(-t * 11)


def _snare(rng) -> np.ndarray:
    t = np.arange(int(0.22 * RATE)) / RATE
    noise = np.diff(_noise(len(t) + 1, rng))  # first difference = high-passed noise
    return (0.7 * noise * np.exp(-t * 24) + 0.5 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 28)) * 0.9


def _hat(rng, open_: bool = False) -> np.ndarray:
    t = np.arange(int((0.22 if open_ else 0.06) * RATE)) / RATE
    n = np.diff(np.diff(_noise(len(t) + 2, rng)))  # second difference: brighter
    return n * np.exp(-t * (16 if open_ else 70)) * 0.5


def _pluck(freq: float, dur: float) -> np.ndarray:
    t = np.arange(int(dur * RATE)) / RATE
    wave_ = sum(np.sin(2 * np.pi * freq * k * t) / k ** 1.3 for k in (1, 2, 3, 4))  # a few soft harmonics
    return wave_ * np.exp(-t * 7) * (1 - np.exp(-t * 400))


def _bass(freq: float, dur: float) -> np.ndarray:
    t = np.arange(int(dur * RATE)) / RATE
    return (np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * freq * 2 * t)) * np.minimum(1, (dur - t) * 30) \
        * np.minimum(1, t * 200)


def _riser(seconds: float, rng) -> np.ndarray:
    n = int(seconds * RATE)
    x = np.linspace(0, 1, n)
    noise = np.diff(_noise(n + 1, rng))
    return noise * x ** 2.2 * 0.5


def _add(buf: np.ndarray, sig: np.ndarray, at: int, gain: float = 1.0) -> None:
    end = min(len(buf), at + len(sig))
    if at < end:
        buf[at:end] += sig[: end - at] * gain


def generate_beat(seconds: float, out_wav: Path, seed: int = 0, style: str = "upbeat") -> Path:
    rng = np.random.default_rng(seed)
    cfg = STYLES[style]
    bpm = cfg["bpm"]
    step = 60 / bpm / 4  # seconds per 16th note
    bar = 16 * step
    n = int(seconds * RATE)
    key = 55.0 * 2 ** (int(rng.integers(0, 12)) / 12)            # A1..G#2 region
    prog = PROGRESSIONS[int(rng.integers(0, len(PROGRESSIONS)))]
    drums, tonal = np.zeros(n), np.zeros(n)
    kick, snare = _kick(), _snare(rng)
    kick_times: list[int] = []
    bars = int(seconds / bar) + 1
    for b in range(bars):
        root_semi, typ = prog[(b // 2) % len(prog)]               # a chord lasts two bars
        root = key * 2 ** (root_semi / 12)
        tones = [root * 4 * 2 ** (s / 12) for s in TRIAD[typ]]    # arp register, two octaves above the root
        fill = (b % 8 == 7)                                       # every 8th bar: build-up
        for s in range(16):
            at = int((b * bar + s * step + (cfg["swing"] * step if s % 2 else 0)) * RATE)
            if at >= n:
                continue
            if cfg["kick"][s] and not (fill and s >= 8):
                _add(drums, kick, at, 1.0)
                kick_times.append(at)
            if cfg["snare"][s] or (fill and s >= 8 and s % 2 == 0):
                _add(drums, snare, at, 0.8 if not fill else 0.55 + 0.03 * s)
            if cfg["hat"][s]:
                _add(drums, _hat(rng, open_=(s % 8 == 6)), at, 0.55 if s % 4 else 0.4)
            if cfg["arp"][s]:
                _add(tonal, _pluck(tones[(s // 2 + b) % 3] if style != "pulse" else tones[s % 3], step * 3), at, cfg["arp_gain"])
            if s % 4 == 0 and (s in (0, 8) or style == "pulse"):
                _add(tonal, _bass(root, step * (6 if s == 0 else 4)), at, cfg["bass_gain"])
        if fill:
            _add(drums, _riser(bar * 0.5, rng), int((b * bar + bar * 0.5) * RATE), 0.7)
    # sidechain pump: everything melodic ducks briefly on each kick
    duck = np.ones(n)
    tail = np.exp(-np.arange(int(0.25 * RATE)) / RATE * 11)
    for at in kick_times:
        end = min(n, at + len(tail))
        duck[at:end] = np.minimum(duck[at:end], 1 - 0.65 * tail[: end - at])
    mix = drums * 0.95 + tonal * duck
    fade = int(1.2 * RATE)
    mix[:fade] *= np.linspace(0, 1, fade)
    mix[-fade:] *= np.linspace(1, 0, fade)
    mix = np.tanh(mix * 1.1)                                       # gentle glue, no hard clipping
    mix *= 0.85 / max(1e-9, np.abs(mix).max())
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes((mix * 32767).astype("<i2").tobytes())
    return out_wav
