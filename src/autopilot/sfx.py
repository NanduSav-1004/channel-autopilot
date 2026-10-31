"""Sound effects for the animated charts (Plotline): soft ticks while numbers count up, a light whoosh as a chart enters, a low accent on text
cards, a small pop when a badge or callout lands. Everything is synthesised here (no samples, so no licence or Content ID question) and
placed at the moments the charts animate (assets/motion/motion.js), then mixed in very quietly UNDER the voice and music."""
import wave
from pathlib import Path

import numpy as np

RATE = 48000
LEVEL = 0.20           # peak of a full-strength effect, as a fraction of full scale (about -14 dBFS); the effects sit under the voice
MIN_START_GAP = 2.5    # seconds between two scene-entry whooshes: a run of short scenes must not sound like a fan


def _t(seconds: float) -> np.ndarray:
    return np.arange(int(seconds * RATE)) / RATE


def _norm(x: np.ndarray) -> np.ndarray:
    return x / max(1e-9, np.abs(x).max())


def tick(pitch: float = 1900.0) -> np.ndarray:
    """A tiny soft click, like a counter wheel."""
    t = _t(0.05)
    return _norm(np.sin(2 * np.pi * pitch * t) * np.exp(-t * 130) + 0.3 * np.sin(2 * np.pi * pitch * 2.1 * t) * np.exp(-t * 220))


def pop() -> np.ndarray:
    """A bubble pop: a short downward pitch glide."""
    t = _t(0.16)
    freq = 640 * np.exp(-t * 7)
    return _norm(np.sin(2 * np.pi * np.cumsum(freq) / RATE) * np.exp(-t * 26))


def accent() -> np.ndarray:
    """A low, soft thump under a text card."""
    t = _t(0.42)
    freq = 120 * np.exp(-t * 4.5) + 45
    return _norm(np.sin(2 * np.pi * np.cumsum(freq) / RATE) * np.exp(-t * 7) * np.minimum(1.0, t * 90))


def _swish(seconds: float, lo: float, hi: float, peak: float, seed: int) -> np.ndarray:
    """Noise ring-modulated by a gliding tone: a band of sound that sweeps from `lo` to `hi` Hz, with a smooth swell."""
    t = _t(seconds)
    rng = np.random.default_rng(seed)
    freq = lo + (hi - lo) * (t / seconds) ** 1.5
    carrier = np.sin(2 * np.pi * np.cumsum(freq) / RATE)
    swell = np.sin(np.pi * np.clip(t / seconds, 0, 1) ** peak) ** 2
    return _norm(rng.standard_normal(len(t)) * carrier * swell)


def whoosh() -> np.ndarray:
    return _swish(0.5, 350.0, 2600.0, 0.8, 1)


def swish(seconds: float) -> np.ndarray:
    """A longer, gentler rising sweep for something that draws or fills over a second or two."""
    return _swish(max(0.4, seconds), 250.0, 1800.0, 1.2, 2) * 0.7


def shimmer(seconds: float = 1.4) -> np.ndarray:
    t = _t(seconds)
    rng = np.random.default_rng(3)
    out = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)) * (0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(2, 5) * t)) for f in (2200, 2960, 3520, 4180))
    return _norm(out * np.sin(np.pi * t / seconds) ** 2) * 0.6


def _ticks(start: float, stop: float, n: int, rising: bool = True, gain: float = 0.5) -> list[tuple[float, str, float]]:
    """n ticks between start and stop, spaced like a count that slows down at the end; pitch rises as the number climbs."""
    out = []
    for k in range(1, n + 1):
        x = k / n
        when = start + (stop - start) * (1 - (1 - x) ** 2)
        out.append((when, f"tick{round(x * 4) if rising else 0}", gain * (0.7 + 0.3 * x)))
    return out


def events_for(spec: dict) -> list[tuple[float, str, float]]:
    """(seconds after the scene starts, sound, strength 0..1) for one chart, timed to its animation in motion.js."""
    typ, dur = spec["type"], spec["duration"]
    ev: list[tuple[float, str, float]] = []
    if typ == "title":
        return [(0.18, "accent", 0.9)]
    ev.append((0.0, "whoosh", 0.55))
    if typ == "counter":
        ev += _ticks(0.3, 2.1, 16) + ([(2.1, "pop", 0.8)] if spec.get("badge") else [])
    elif typ in ("bars", "slope"):
        ev += [(0.45 + i * (0.12 if typ == "bars" else 0.16), "tick2", 0.5) for i in range(min(10, len(spec.get("items", []))))]
    elif typ == "race":
        ev.append((0.9, f"swish:{max(1.0, dur - 2.2):.2f}", 0.55))
    elif typ == "compare":
        ev += [(0.6, "swish:1.2", 0.5), (1.5, "swish:1.2", 0.5), (3.0, "pop", 0.8)]
    elif typ in ("line", "multiline", "stacked"):
        ev.append((0.6, f"swish:{min(spec.get('draw', 4.0), max(1.0, dur - 1.0)):.2f}", 0.5))
    elif typ in ("map", "world_map"):
        ev += [(0.5, "swish:1.8", 0.55), (2.8, "pop", 0.8)]
    elif typ == "kpi":
        ev += [(0.5 + i * 0.18, "tick2", 0.55) for i in range(len(spec.get("cards", [])))] + _ticks(0.5, 2.1, 10, gain=0.35)
    elif typ == "waffle":
        ev += _ticks(0.4, 2.6, 18, gain=0.4)
    elif typ == "gauge":
        ev += [(0.5, "swish:2.0", 0.5), (2.5, "pop", 0.8)]
    elif typ == "donut":
        ev.append((0.4, "swish:1.8", 0.5))
    elif typ == "heatmap":
        ev.append((0.4, "shimmer", 0.5))
    elif typ == "scatter":
        ev += [(1.9, "swish:0.9", 0.4), (2.5, "pop", 0.7)]
    return [e for e in ev if e[0] < dur - 0.1]


def _sound(name: str) -> np.ndarray:
    kind, _, arg = name.partition(":")
    if kind.startswith("tick"):
        return tick(1500 + 220 * int(kind[4:] or 0))
    return {"pop": pop, "accent": accent, "whoosh": whoosh, "shimmer": shimmer}.get(kind, lambda: swish(float(arg or 1.0)))()


def track_events(specs: list[dict], starts: list[float]) -> list[tuple[float, str, float]]:
    """All events of a video at absolute times. A scene-entry whoosh is skipped when the last one was under MIN_START_GAP seconds ago."""
    out, last_whoosh = [], -99.0
    for spec, start in zip(specs, starts, strict=True):
        for off, name, gain in events_for(spec):
            if name == "whoosh":
                if start - last_whoosh < MIN_START_GAP:
                    continue
                last_whoosh = start
            out.append((start + off, name, gain))
    return out


def render_track(events: list[tuple[float, str, float]], seconds: float, out_wav: Path) -> Path:
    """Place the events on a silent track of `seconds` and write it (48 kHz, mono, 16 bit)."""
    mix = np.zeros(int((seconds + 1.0) * RATE))
    cache: dict[str, np.ndarray] = {}
    for when, name, gain in events:
        snd = cache.setdefault(name, _sound(name))
        i = int(when * RATE)
        if i < 0 or i >= len(mix):
            continue
        end = min(len(mix), i + len(snd))
        mix[i:end] += snd[: end - i] * gain * LEVEL
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    _write(out_wav, mix)
    return out_wav


def _read(path: Path) -> np.ndarray:
    with wave.open(str(path)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float64) / 32768


def _write(path: Path, x: np.ndarray) -> None:
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())


def add_to_mix(mixed: Path, track: Path, out_wav: Path) -> Path:
    """Add the effects to the finished voice-and-music mix (48 kHz mono). They only ADD sound, so the voice cannot be lost;
    the result is scaled down if it would exceed 0.97 of full scale."""
    a, b = _read(mixed), _read(track)
    n = len(a)
    b = np.pad(b, (0, max(0, n - len(b))))[:n]
    out = a + b
    peak = float(np.abs(out).max())
    if peak > 0.97:
        out *= 0.97 / peak
    _write(out_wav, out)
    return out_wav
