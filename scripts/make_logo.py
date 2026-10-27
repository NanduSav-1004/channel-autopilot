"""Channel logos (800x800), drawn in code: a bright four-point spark inside two crossing electron orbits, in a ring.
No letters, so the same mark works for every language; the English channel is navy, the Malayalam channel teal.

usage: python scripts/make_logo.py   -> assets/brand/icon.png and assets/brand_ml/icon.png
YouTube shows the picture as a circle, so everything important sits well inside it.
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

S = 1600
AMBER, WHITE_HOT, ORANGE = (255, 196, 48), (255, 250, 228), (255, 140, 40)


def background(inner: tuple, outer: tuple) -> Image.Image:
    y, x = np.mgrid[0:S, 0:S]
    d = np.clip(np.hypot(x - S / 2, y - S / 2) / (S * 0.72), 0, 1) ** 1.2
    arr = np.stack([inner[c] + (outer[c] - inner[c]) * d for c in range(3)], axis=-1)
    return Image.fromarray(arr.astype("uint8")).convert("RGBA")


def spark(radius: float, concave: float = 0.72) -> Image.Image:
    """A four-point star with concave sides (a superellipse), filled white-hot at the heart, amber, orange at the tips."""
    y, x = np.mgrid[0:S, 0:S].astype(float)
    nx, ny = np.abs(x - S / 2) / radius, np.abs(y - S / 2) / radius
    inside = (nx ** concave + ny ** concave) <= 1.0
    r = np.hypot(nx, ny)
    t = np.clip(r, 0, 1.2)
    col = np.zeros((S, S, 4))
    for c in range(3):
        core = WHITE_HOT[c] * np.clip(1 - t / 0.35, 0, 1)
        mid = AMBER[c] * np.clip(1 - np.abs(t - 0.35) / 0.65, 0, 1)
        tip = ORANGE[c] * np.clip((t - 0.35) / 0.65, 0, 1)
        col[..., c] = np.clip(core + mid + tip, 0, 255)
    col[..., 3] = inside * 255
    img = Image.fromarray(col.astype("uint8"), "RGBA")
    return img.filter(ImageFilter.GaussianBlur(1.2))


def orbit(img: Image.Image, angle: float, colour: tuple, electron_at: float) -> None:
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rx, ry = S * 0.40, S * 0.145
    d.ellipse([S / 2 - rx, S / 2 - ry, S / 2 + rx, S / 2 + ry], outline=colour + (235,), width=int(S * 0.016))
    ex, ey = S / 2 + rx * math.cos(electron_at), S / 2 + ry * math.sin(electron_at)
    g = S * 0.034
    halo = Image.new("RGBA", (S, S), (0, 0, 0, 0))                      # a soft glow, not a hard disc
    ImageDraw.Draw(halo).ellipse([ex - g * 2.2, ey - g * 2.2, ex + g * 2.2, ey + g * 2.2], fill=(255, 215, 110, 200))
    layer.alpha_composite(halo.filter(ImageFilter.GaussianBlur(g * 0.9)))
    d = ImageDraw.Draw(layer)
    d.ellipse([ex - g, ey - g, ex + g, ey + g], fill=(255, 205, 70, 255))
    d.ellipse([ex - g * 0.45, ey - g * 0.45, ex + g * 0.45, ey + g * 0.45], fill=(255, 250, 225, 255))
    img.alpha_composite(layer.rotate(angle, resample=Image.BICUBIC, center=(S / 2, S / 2)))


def logo(inner: tuple, outer: tuple, orbit_colour: tuple, ring: tuple, out: Path) -> None:
    img = background(inner, outer)
    d = ImageDraw.Draw(img)
    r = S * 0.465
    d.ellipse([S / 2 - r, S / 2 - r, S / 2 + r, S / 2 + r], outline=ring + (255,), width=int(S * 0.014))
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([S * 0.28, S * 0.28, S * 0.72, S * 0.72], fill=AMBER + (120,))
    back = img.copy()
    orbit(back, 28, orbit_colour, math.radians(210))       # the far orbit passes behind the spark
    orbit(back, -28, orbit_colour, math.radians(40))
    back.alpha_composite(glow.filter(ImageFilter.GaussianBlur(S * 0.08)))
    img = back
    img.alpha_composite(spark(S * 0.30))
    img.convert("RGB").resize((800, 800), Image.LANCZOS).save(out)


def circle_preview(path: Path, size: int, out: Path) -> None:
    im = Image.open(path).convert("RGB").resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size - 1, size - 1], fill=255)
    bg = Image.new("RGB", (size, size), (255, 255, 255))
    bg.paste(im, mask=mask)
    bg.save(out)


if __name__ == "__main__":
    Path("assets/brand").mkdir(parents=True, exist_ok=True)
    Path("assets/brand_ml").mkdir(parents=True, exist_ok=True)
    logo((30, 52, 118), (5, 10, 30), (214, 232, 255), AMBER, Path("assets/brand/icon.png"))
    logo((10, 96, 112), (3, 20, 34), (190, 245, 235), AMBER, Path("assets/brand_ml/icon.png"))
    print("wrote assets/brand/icon.png and assets/brand_ml/icon.png")
