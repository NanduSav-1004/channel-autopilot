"""A small animated mascot that talks along with the narration: its mouth follows the voice's loudness, it blinks and bobs.
Two characters: "bulb" (Beam, a friendly light bulb) and "atom" (Orbit, a nucleus with electrons circling it). Drawn in code (no assets, no GPU), rendered as a transparent video track and overlaid in the
final pass. It works for any language because it listens to the audio, not the words."""
import math
import subprocess
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

NAVY, STEEL, AMBER, GLOW = (14, 27, 61), (74, 90, 128), (255, 190, 40), (255, 214, 102)
SS = 4                      # drawn at 4x, shown at 1x: smooth edges
FPS = 24                    # the same rate as the video, so the overlay never has to guess which frame to show
TAIL_SECONDS = 2.0          # the track runs a little past the narration, so the character never vanishes before the video ends


def _glass(size: int) -> Image.Image:
    """The bulb: a glowing amber glass globe tapering into a navy screw base."""
    s = size * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy, r = s // 2, int(s * 0.42), int(s * 0.34)
    halo = Image.new("RGBA", (s, s), (0, 0, 0, 0))                       # soft glow behind the glass
    ImageDraw.Draw(halo).ellipse([cx - r * 1.18, cy - r * 1.18, cx + r * 1.18, cy + r * 1.18], fill=GLOW + (70,))   # inside the canvas: no hard edge
    img.alpha_composite(halo.filter(ImageFilter.GaussianBlur(s * 0.05)))
    d.polygon([(cx - r * 0.62, cy + r * 0.62), (cx + r * 0.62, cy + r * 0.62), (cx + r * 0.36, cy + r * 1.22),
               (cx - r * 0.36, cy + r * 1.22)], fill=AMBER)             # the neck
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=AMBER)             # the globe
    d.ellipse([cx - r * 0.86, cy - r * 0.86, cx + r * 0.86, cy + r * 0.86], fill=GLOW)   # lighter core
    d.arc([cx - r * 0.74, cy - r * 0.74, cx + r * 0.74, cy + r * 0.74], 200, 250, fill=(255, 250, 225), width=int(s * 0.022))
    d.ellipse([cx - r * 0.55, cy - r * 0.72, cx - r * 0.36, cy - r * 0.55], fill=(255, 252, 235))   # a shine
    for k in range(3):                                                    # the screw base
        y0 = cy + r * (1.2 + 0.13 * k)
        d.rounded_rectangle([cx - r * (0.42 - 0.02 * k), y0, cx + r * (0.42 - 0.02 * k), y0 + r * 0.11], radius=int(s * 0.012),
                            fill=NAVY if k % 2 == 0 else STEEL)
    d.pieslice([cx - r * 0.2, cy + r * 1.55, cx + r * 0.2, cy + r * 1.75], 0, 180, fill=NAVY)
    return img


def _face(size: int, mouth: int, blink: bool, centre: tuple[float, float] = (0.5, 0.42), radius: float = 0.34) -> Image.Image:
    s = size * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy, r = int(s * centre[0]), int(s * centre[1]), int(s * radius)
    ex, ey, er = r * 0.38, cy - r * 0.12, r * 0.17
    for sign in (-1, 1):
        x = cx + sign * ex
        if blink:
            d.arc([x - er, ey - er * 0.3, x + er, ey + er * 0.9], 200, 340, fill=NAVY, width=int(s * 0.018))
        else:
            d.ellipse([x - er, ey - er * 1.15, x + er, ey + er * 1.15], fill=(255, 255, 255))
            d.ellipse([x - er * 0.55, ey - er * 0.5, x + er * 0.55, ey + er * 0.85], fill=NAVY)
            d.ellipse([x - er * 0.25, ey - er * 0.35, x + er * 0.05, ey - er * 0.05], fill=(255, 255, 255))
        d.arc([x - er * 1.2, ey - er * 2.1, x + er * 1.2, ey - er * 0.6], 200, 340, fill=NAVY, width=int(s * 0.014))   # brow
    for sign in (-1, 1):                                                   # cheeks
        x = cx + sign * r * 0.62
        d.ellipse([x - r * 0.1, cy + r * 0.2, x + r * 0.1, cy + r * 0.34], fill=(255, 150, 90, 150))
    my = cy + r * 0.34
    if mouth == 0:                                                         # closed: a small smile
        d.arc([cx - r * 0.2, my - r * 0.12, cx + r * 0.2, my + r * 0.16], 20, 160, fill=NAVY, width=int(s * 0.02))
    else:
        w, h = (0.11, 0.07) if mouth == 1 else (0.17, 0.13) if mouth == 2 else (0.2, 0.2)
        d.ellipse([cx - r * w, my - r * h * 0.6, cx + r * w, my + r * h * 1.4], fill=NAVY)
        if mouth >= 2:
            d.ellipse([cx - r * w * 0.55, my + r * h * 0.55, cx + r * w * 0.55, my + r * h * 1.35], fill=(235, 110, 110))
    return img


ORBITS = (0, 60, 120)       # degrees
PHASES = 30                 # electron positions in one lap


def _atom(size: int, phase: int) -> tuple[Image.Image, Image.Image]:
    """(everything behind the face, electrons in front of it): a blue nucleus ball with three tilted orbits and amber electrons."""
    s = size * SS
    back = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    front = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    c, rx, ry, nr = s / 2, s * 0.44, s * 0.16, s * 0.27
    glow = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([c - nr * 1.5, c - nr * 1.5, c + nr * 1.5, c + nr * 1.5], fill=(110, 190, 255, 70))
    back.alpha_composite(glow.filter(ImageFilter.GaussianBlur(s * 0.05)))
    for k, deg in enumerate(ORBITS):
        ring = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        ImageDraw.Draw(ring).ellipse([c - rx, c - ry, c + rx, c + ry], outline=(214, 232, 255, 200), width=int(s * 0.014))
        back.alpha_composite(ring.rotate(deg, resample=Image.BICUBIC, center=(c, c)))
    nd = ImageDraw.Draw(back)
    nd.ellipse([c - nr, c - nr, c + nr, c + nr], fill=(70, 150, 255))
    nd.ellipse([c - nr * 0.9, c - nr * 0.9, c + nr * 0.9, c + nr * 0.9], fill=(120, 185, 255))
    nd.arc([c - nr * 0.78, c - nr * 0.78, c + nr * 0.78, c + nr * 0.78], 200, 250, fill=(235, 245, 255), width=int(s * 0.02))
    for k, deg in enumerate(ORBITS):                                  # an electron on each orbit
        ang = 2 * math.pi * (phase / PHASES + k / 3)
        x0, y0 = rx * math.cos(ang), ry * math.sin(ang)
        a = math.radians(deg)
        x, y = c + x0 * math.cos(a) - y0 * math.sin(a), c + x0 * math.sin(a) + y0 * math.cos(a)
        g = s * 0.035
        layer = front if math.sin(ang) > 0 else back                  # the far half of the orbit passes behind the ball
        ed = ImageDraw.Draw(layer)
        ed.ellipse([x - g * 1.8, y - g * 1.8, x + g * 1.8, y + g * 1.8], fill=AMBER + (80,))
        ed.ellipse([x - g, y - g, x + g, y + g], fill=AMBER)
    return back, front


_cache: dict = {}


def sprite(size: int, mouth: int, blink: bool, style: str = "bulb", phase: int = 0) -> Image.Image:
    phase = phase % PHASES if style == "atom" else 0
    key = (size, mouth, blink, style, phase)
    if key not in _cache:
        if style == "atom":
            img, front = _atom(size, phase)
            img.alpha_composite(_face(size, mouth, blink, (0.5, 0.5), 0.27))
            img.alpha_composite(front)
        else:
            img = _glass(size)
            img.alpha_composite(_face(size, mouth, blink))
        _cache[key] = img.resize((size, size), Image.LANCZOS)
    return _cache[key]


def mouth_levels(wav_path: Path, fps: int = FPS) -> list[int]:
    """Mouth opening 0-3 for every video frame, from the loudness of the voice: smoothed, with a little hysteresis so the
    mouth does not flutter."""
    with wave.open(str(wav_path)) as w:
        rate = w.getframerate()
        a = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(float)
    n = max(1, rate // fps)
    k = len(a) // n
    rms = np.sqrt((a[: k * n].reshape(k, n) ** 2).mean(axis=1)) if k else np.zeros(0)
    if not k:
        return []
    top = float(np.percentile(rms, 95)) or 1.0
    x = np.convolve(rms / top, np.ones(3) / 3 if fps > 16 else [0.25, 0.5, 0.25], mode="same")
    levels, cur = [], 0
    for v in x:
        want = 0 if v < 0.10 else 1 if v < 0.38 else 2 if v < 0.7 else 3
        cur = want if abs(want - cur) > 1 or (want > cur) or v < 0.06 else cur - (1 if want < cur else 0)
        levels.append(cur)
    return levels


def blink_frames(count: int, fps: int = FPS, seed: int = 7) -> set[int]:
    rng = np.random.default_rng(seed)
    out, t = set(), rng.uniform(1.5, 3.0)
    while t * fps < count:
        f = int(t * fps)
        out |= {f, f + 1}
        t += rng.uniform(2.5, 5.0)
    return out


def render_track(narration: Path, out: Path, size: int = 260, fps: int = FPS, seed: int = 7, style: str = "bulb") -> Path:
    """A transparent video (QuickTime Animation, alpha) of the mascot talking along with `narration`."""
    levels = mouth_levels(narration, fps) + [0] * int(TAIL_SECONDS * fps)
    blinks = blink_frames(len(levels), fps, seed)
    pad = int(size * 0.08)
    canvas = size + pad
    cmd = ["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{canvas}x{canvas}", "-r", str(fps),
           "-i", "-", "-c:v", "qtrle", "-pix_fmt", "argb", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    prev = None
    for i, lv in enumerate(levels):
        speaking = lv > 0
        bob = round(math.sin(i / fps * 2 * math.pi * 1.1) * pad * 0.35 * (1.0 if speaking else 0.4))
        frame = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
        frame.alpha_composite(sprite(size, lv, i in blinks, style, i * 12 // fps), (pad // 2, pad // 2 + bob))
        raw = frame.tobytes()
        proc.stdin.write(raw)
        prev = raw
    proc.stdin.close()
    if proc.wait() != 0 or prev is None:
        raise OSError("could not render the mascot track")
    return out
