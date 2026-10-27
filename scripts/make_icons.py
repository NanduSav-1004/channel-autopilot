"""Channel icons (800x800) built around the mascot: Beam the light bulb on a glowing background.

usage: python scripts/make_icons.py        -> assets/brand/icon.png (English) and assets/brand_ml/icon.png (Malayalam)
YouTube shows the icon as a circle, so everything important stays well inside it.
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, "src")
from autopilot import mascot

S = 1600
AMBER, NAVY = (255, 190, 40), (14, 27, 61)
FONT_ML = "/usr/share/fonts/truetype/noto/NotoSansMalayalam-Bold.ttf"


def background(inner: tuple, outer: tuple) -> Image.Image:
    y, x = np.mgrid[0:S, 0:S]
    d = np.clip(np.hypot(x - S / 2, y - S * 0.46) / (S * 0.62), 0, 1) ** 1.3
    arr = np.zeros((S, S, 3))
    for c in range(3):
        arr[..., c] = inner[c] + (outer[c] - inner[c]) * d
    return Image.fromarray(arr.astype("uint8")).convert("RGBA")


def rings(img: Image.Image, colour: tuple) -> None:
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for k, r in enumerate((560, 700, 840)):
        d.ellipse([S / 2 - r, S / 2 - r * 0.42, S / 2 + r, S / 2 + r * 0.42], outline=colour + (46 - k * 10,), width=6)
    img.alpha_composite(layer.rotate(-24, resample=Image.BICUBIC, center=(S / 2, S / 2)))


def rays(img: Image.Image) -> None:
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = S / 2, S * 0.43
    for i in range(14):
        a = math.radians(-90 + (i - 6.5) * 21)
        r0, r1 = S * 0.27, S * (0.305 if i % 2 else 0.325)
        d.line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))],
               fill=AMBER + (210,), width=int(S * 0.016))
    img.alpha_composite(layer)


def sparkle(img: Image.Image, x: float, y: float, r: float, colour=(255, 255, 255)) -> None:
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.polygon([(x, y - r), (x + r * 0.22, y - r * 0.22), (x + r, y), (x + r * 0.22, y + r * 0.22), (x, y + r),
               (x - r * 0.22, y + r * 0.22), (x - r, y), (x - r * 0.22, y - r * 0.22)], fill=colour + (235,))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(1.5)))


def badge(img: Image.Image, letter: str) -> None:
    d = ImageDraw.Draw(img)
    r, cx, cy = int(S * 0.125), int(S * 0.735), int(S * 0.715)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=NAVY, outline=AMBER, width=int(S * 0.012))
    font = ImageFont.truetype(FONT_ML, int(r * 1.25))
    bb = d.textbbox((0, 0), letter, font=font)
    d.text((cx - (bb[0] + bb[2]) / 2, cy - (bb[1] + bb[3]) / 2 - r * 0.04), letter, font=font, fill=(255, 255, 255))


def icon(inner: tuple, outer: tuple, ring: tuple, out: Path, letter: str | None = None) -> None:
    img = background(inner, outer)
    rings(img, ring)
    rays(img)
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([S * 0.2, S * 0.14, S * 0.8, S * 0.74], fill=(255, 214, 102, 95))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(S * 0.07)))
    size = 1060
    bulb = mascot.sprite(size, 0, False)                       # the friendly closed smile
    img.alpha_composite(bulb, ((S - size) // 2, int(S * 0.44 - size * 0.45)))
    for x, y, r in ((0.2, 0.2, 60), (0.82, 0.24, 44), (0.15, 0.62, 36), (0.86, 0.5, 30)):
        sparkle(img, S * x, S * y, r)
    if letter:
        badge(img, letter)
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
    icon((34, 58, 125), (5, 10, 30), (214, 232, 255), Path("assets/brand/icon.png"))
    icon((12, 104, 122), (4, 22, 38), (190, 245, 240), Path("assets/brand_ml/icon.png"), letter="ബ")
    print("wrote assets/brand/icon.png and assets/brand_ml/icon.png")
