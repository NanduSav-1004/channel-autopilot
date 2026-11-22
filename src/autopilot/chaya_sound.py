"""Sound design for Science Chaya videos: cut sounds (whoosh, swipe, impact), a riser into each reveal, ticks on beats, counters, stamps and dings,
a thunder crack for lightning, quiet ambience beds that match the picture (rain, birds, crickets, wind, crowd, water, machine hum) and a soft low
pulse under the hook. Everything is synthesised here (no samples: no licence or Content ID question) and mixed in UNDER the voice.
`events_for(spec)` plans it from the storyboard; `render(...)` writes the track that `sfx.add_to_mix` adds to the voice-and-music mix."""
import wave
import zlib
from pathlib import Path

import numpy as np

RATE = 48000
LEVEL = 0.52          # peak of a full-strength effect (the old kit used 0.20): the references this style follows carry about 2.5 times more low end
AMB_LEVEL = 0.07      # ambience beds stay far below the voice


def _t(sec: float) -> np.ndarray:
    return np.arange(int(sec * RATE)) / RATE


def _norm(x: np.ndarray) -> np.ndarray:
    return x / max(1e-9, np.abs(x).max())


def _noise(sec: float, seed: int) -> np.ndarray:
    return np.random.default_rng(seed).standard_normal(int(sec * RATE))


def _fft_band(x: np.ndarray, lo: float, hi: float) -> np.ndarray:
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / RATE)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))


def boom(sec: float = 0.8, f0: float = 70.0) -> np.ndarray:
    t = _t(sec)
    body = np.sin(2 * np.pi * np.cumsum(f0 * np.exp(-t * 5) + 32) / RATE) * np.exp(-t * 5.5)
    crack = _fft_band(_noise(sec, 11), 80, 900) * np.exp(-t * 28) * 0.5
    return _norm((body + crack) * np.minimum(1, t * 400))


def impact() -> np.ndarray:
    t = _t(0.9)
    return _norm(boom(0.9, 90) * 0.9 + _fft_band(_noise(0.9, 12), 1500, 6000) * np.exp(-t * 40) * 0.5)


def whoosh(sec: float = 0.42) -> np.ndarray:
    t = _t(sec)
    n = _fft_band(_noise(sec, 13), 300, 5500)
    sweep = np.sin(np.pi * np.clip(t / sec, 0, 1) ** 0.9) ** 2
    return _norm(n * sweep)


def swipe() -> np.ndarray:
    t = _t(0.22)
    return _norm(_fft_band(_noise(0.22, 14), 1800, 9000) * np.sin(np.pi * t / 0.22) ** 1.5)


def riser(sec: float = 1.0) -> np.ndarray:
    t = _t(sec)
    n = _fft_band(_noise(sec, 15), 500, 7000) * (t / sec) ** 2.2
    tone = np.sin(2 * np.pi * np.cumsum(220 + 1400 * (t / sec) ** 2) / RATE) * (t / sec) ** 2.6 * 0.5
    return _norm(n + tone) * np.minimum(1, (sec - t) * 40 + 0.0)


def pop() -> np.ndarray:
    t = _t(0.16)
    return _norm(np.sin(2 * np.pi * np.cumsum(700 * np.exp(-t * 7)) / RATE) * np.exp(-t * 26))


def tick(pitch: float = 2000.0) -> np.ndarray:
    t = _t(0.05)
    return _norm(np.sin(2 * np.pi * pitch * t) * np.exp(-t * 120))


def click() -> np.ndarray:
    t = _t(0.03)
    return _norm(_fft_band(_noise(0.03, 16), 2500, 8000) * np.exp(-t * 160))


def stamp() -> np.ndarray:
    t = _t(0.55)
    thud = np.sin(2 * np.pi * np.cumsum(120 * np.exp(-t * 9) + 40) / RATE) * np.exp(-t * 10)
    return _norm(thud + _fft_band(_noise(0.55, 17), 300, 4000) * np.exp(-t * 45) * 0.7)


def ding() -> np.ndarray:
    t = _t(0.9)
    return _norm((np.sin(2 * np.pi * 1318 * t) + 0.6 * np.sin(2 * np.pi * 1976 * t) + 0.3 * np.sin(2 * np.pi * 2637 * t)) * np.exp(-t * 4.5))


def buzz() -> np.ndarray:
    t = _t(0.38)
    return _norm(np.sign(np.sin(2 * np.pi * 140 * t)) * 0.6 * np.sin(np.pi * np.clip(t / 0.38, 0, 1)) + np.sin(2 * np.pi * 70 * t) * 0.4)


def coin() -> np.ndarray:
    t = _t(0.5)
    return _norm((np.sin(2 * np.pi * 1760 * t) * (t < 0.08) + np.sin(2 * np.pi * 2349 * t) * (t >= 0.08)) * np.exp(-t * 7))


def shimmer(sec: float = 1.2) -> np.ndarray:
    t = _t(sec)
    rng = np.random.default_rng(3)
    out = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)) * (0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(2, 5) * t)) for f in (2200, 2960, 3520, 4180))
    return _norm(out * np.sin(np.pi * t / sec) ** 2) * 0.6


def thunder(sec: float = 2.6) -> np.ndarray:
    t = _t(sec)
    rumble = _fft_band(_noise(sec, 18), 30, 220) * (np.exp(-t * 1.1) * (0.4 + 0.6 * np.abs(np.sin(t * 5.3))))
    return _norm(rumble) * np.minimum(1, t * 30)


def crack() -> np.ndarray:
    t = _t(0.35)
    return _norm(_fft_band(_noise(0.35, 19), 1200, 10000) * np.exp(-t * 18)) * 0.9


SOUNDS = {"boom": boom, "impact": impact, "whoosh": whoosh, "swipe": swipe, "riser": riser, "pop": pop, "tick": tick, "click": click, "stamp": stamp,
          "ding": ding, "buzz": buzz, "coin": coin, "shimmer": shimmer, "thunder": thunder, "crack": crack}


def _sound(name: str) -> np.ndarray:
    kind, _, arg = name.partition(":")
    fn = SOUNDS[kind]
    if kind == "riser" and arg:
        return fn(float(arg))
    if kind == "tick" and arg:
        return fn(1500 + 180 * int(arg))
    return fn()


# ---------- ambience beds: quiet, looping texture under a scene ----------
def ambience(kind: str, sec: float) -> np.ndarray:
    n = int(sec * RATE)
    t = _t(sec)
    rng = np.random.default_rng(zlib.crc32(kind.encode()) % 10000)
    if kind == "rain":
        x = _fft_band(rng.standard_normal(n), 2000, 9000) * 0.6
        for _ in range(int(sec * 40)):
            i = rng.integers(0, max(1, n - 400)); x[i:i + 400] += np.exp(-np.arange(400) / 60) * rng.uniform(0.3, 1.0) * np.sin(2 * np.pi * rng.uniform(1500, 4000) * np.arange(400) / RATE)
    elif kind == "wind":
        x = _fft_band(rng.standard_normal(n), 120, 900) * (0.55 + 0.45 * np.sin(2 * np.pi * 0.17 * t + 1))
    elif kind == "crowd":
        x = _fft_band(rng.standard_normal(n), 250, 1400) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.6 * t) ** 2)
    elif kind == "crickets":
        x = np.sin(2 * np.pi * 4300 * t) * (np.sin(2 * np.pi * 38 * t) > 0.2) * (0.5 + 0.5 * np.sin(2 * np.pi * 1.3 * t)) * 0.5
        x += np.sin(2 * np.pi * 5100 * t) * (np.sin(2 * np.pi * 31 * t + 1) > 0.3) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.9 * t + 2)) * 0.4
    elif kind == "birds":
        x = np.zeros(n)
        for _ in range(int(sec * 0.9)):
            i = rng.integers(0, max(1, n - 12000)); L = int(rng.uniform(0.08, 0.25) * RATE); tt = np.arange(L) / RATE
            x[i:i + L] += np.sin(2 * np.pi * np.cumsum(rng.uniform(2200, 3800) + 1500 * np.sin(2 * np.pi * rng.uniform(8, 20) * tt)) / RATE) * np.sin(np.pi * tt / (L / RATE)) * 0.7
        x += _fft_band(rng.standard_normal(n), 100, 500) * 0.1
    elif kind == "water":
        x = _fft_band(rng.standard_normal(n), 200, 2200) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.35 * t + np.sin(2 * np.pi * 0.11 * t) * 3)) ** 1.5
    elif kind == "hum":
        x = np.sin(2 * np.pi * 100 * t) + 0.5 * np.sin(2 * np.pi * 200 * t) + 0.25 * np.sin(2 * np.pi * 300 * t)
        x += _fft_band(rng.standard_normal(n), 400, 1800) * 0.08
    else:
        return np.zeros(n)
    x = _norm(x)
    fade = np.minimum(1, np.minimum(t, sec - t) / 0.5)
    return x * fade


def pulse(sec: float, bpm: float = 104.0) -> np.ndarray:
    """A soft kick on every beat, only meant for a few seconds under the hook."""
    out = np.zeros(int(sec * RATE))
    step, k = 60.0 / bpm, boom(0.38, 62)
    t = 0.0
    while t < sec - 0.4:
        i = int(t * RATE)
        out[i:i + len(k)] += k[:len(out) - i] * (1.0 if int(t / step) % 4 == 0 else 0.7)
        t += step
    fade = np.minimum(1, np.minimum(np.arange(len(out)) / RATE, sec - np.arange(len(out)) / RATE) / 0.6)
    return out * fade


# ---------- planning from the storyboard ----------
AMB_BY_LAYER = {"rain": "rain", "fireflies": "crickets", "bubbles": None}
AMB_BY_KIND = {"terrain": "wind", "map": "wind", "generator": "hum", "transformer": "hum", "dam": "water", "bird": "birds", "tea": "hum"}


def ambience_for(scene: dict) -> str | None:
    """Which bed suits a scene: rain particles mean rain, fireflies mean crickets, a bolt means a storm; some scene kinds have their own."""
    p = scene.get("p", {})
    kinds = {(lay.get("t"), lay.get("kind")) for lay in p.get("layers", [])}
    if ("particles", "rain") in kinds or p.get("bg") == "storm":
        return "rain"
    if ("particles", "fireflies") in kinds and p.get("bg") == "night":
        return "crickets"
    return AMB_BY_KIND.get(scene["kind"])


def events_for(spec: dict) -> tuple[list[tuple[float, str, float]], list[tuple[float, float, str, float]]]:
    """(events [(time, sound, gain)], beds [(start, end, kind, gain)]) for a video."""
    ev: list[tuple[float, str, float]] = [(0.0, "impact", 0.7)]
    beats = spec.get("beats", [])
    scenes = spec["scenes"]
    for k, sc in enumerate(scenes):
        t0, tr = sc["t0"], sc.get("tr", "cut")
        if k > 0:
            if sc["kind"] in ("stat", "meter", "flow", "bars"):
                ev.append((t0 - 0.85, "riser:0.85", 0.45))
            ev.append((t0, {"whip": "whoosh", "zoom": "impact", "flash": "swipe"}.get(tr, "swipe"), 0.55 if tr != "cut" else 0.4))
        if sc["kind"] == "stat":
            ev += [(t0 + 0.4 + i * 0.12, f"tick:{i % 8}", 0.22) for i in range(14)] + [(t0 + 2.2, "ding", 0.5)]
        if sc["kind"] == "bars":
            ev += [(t0 + 0.5, "whoosh", 0.4), (t0 + 2.0, "pop", 0.5)]
        if sc["kind"] == "text":
            ev.append((t0 + 0.12, "boom", 0.6))
        if sc["kind"] == "outro":
            ev += [(t0 + 0.3, "ding", 0.55), (t0 + 1.0, "shimmer", 0.4)]
        d = sc["t1"] - t0
        for lay in sc.get("p", {}).get("layers", []):
            at = t0 + lay.get("at", 0) * d
            if lay.get("t") == "bolt":
                ev += [(at, "crack", 0.8), (at + 0.1, "thunder", 0.9)]
            elif lay.get("t") == "rings":
                ev.append((at, "boom", 0.35))
            elif lay.get("t") == "flash":
                ev.append((at, "impact", 0.6))
            elif lay.get("t") == "icon" and lay.get("at", 0) > 0.02:
                ev.append((at, "pop", 0.45))
    ev += [(b, "click", 0.22) for b in beats]
    ev += [(cd["t0"], "pop", 0.3) for cd in spec["cards"]]
    # at most one cut sound within 0.35 s of another (a hard cut and a riser peak must not pile up)
    ev.sort()
    beds = []
    for sc in scenes:
        kind = ambience_for(sc)
        if kind:
            beds.append((sc["t0"], sc["t1"], kind, 1.0))
    return [e for e in ev if e[0] < spec["duration"] - 0.05], beds


def render(spec: dict, out_wav: Path, hook_pulse: float = 9.0) -> Path:
    """The whole effects track of a video: placed events, ambience beds, and a soft pulse under the hook."""
    total = spec["duration"]
    mix = np.zeros(int((total + 1.0) * RATE))
    events, beds = events_for(spec)
    cache: dict[str, np.ndarray] = {}
    for when, name, gain in events:
        snd = cache.setdefault(name, _sound(name))
        i = int(max(0.0, when) * RATE)
        if i >= len(mix):
            continue
        end = min(len(mix), i + len(snd))
        mix[i:end] += snd[: end - i] * gain * LEVEL
    for a, b, kind, gain in beds:
        bed = ambience(kind, max(1.0, b - a)) * gain * AMB_LEVEL
        i = int(a * RATE)
        end = min(len(mix), i + len(bed))
        mix[i:end] += bed[: end - i]
    if hook_pulse > 0:
        p = pulse(hook_pulse) * 0.22
        mix[: len(p)] += p
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes((np.clip(mix, -1, 1) * 32767).astype("<i2").tobytes())
    return out_wav
