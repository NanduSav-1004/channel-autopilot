"""Generate the channel logo (800x800) and banner (2560x1440) for a given name.

usage: python scripts/make_brand.py "Brightwork Science" "How the world really works"
Drawn at 4x and downsampled for clean edges. Banner text stays inside YouTube's 1546x423 safe area.
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

NAVY, DEEP = (14, 27, 61), (7, 14, 36)
AMBER, ICE = (255, 183, 51), (214, 232, 255)
FONT = "/usr/share/fonts/truetype/lato/Lato-Bold.ttf"
FONT_LIGHT = "/usr/share/fonts/truetype/lato/Lato-Medium.ttf"
SS = 4  # supersampling factor
SAFE_W = 1500  # banner content width limit (YouTube safe area is 1546 px)


def mark(size: int, letter: str) -> Image.Image:
    """The emblem: a ringed monogram with an orbit and a bright spark."""
    s = size * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = s // 2
    r = int(s * 0.46)
    d.ellipse([c - r, c - r, c + r, c + r], fill=NAVY)
    d.ellipse([c - r, c - r, c + r, c + r], outline=AMBER, width=int(s * 0.022))
    # orbit ellipse, tilted, behind the letter
    orbit = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    od = ImageDraw.Draw(orbit)
    rx, ry = int(s * 0.40), int(s * 0.15)
    od.ellipse([c - rx, c - ry, c + rx, c + ry], outline=ICE + (150,), width=int(s * 0.012))
    orbit = orbit.rotate(-28, resample=Image.BICUBIC, center=(c, c))
    img.alpha_composite(orbit)
    font = ImageFont.truetype(FONT, int(s * 0.52))
    bb = d.textbbox((0, 0), letter, font=font)
    d.text((c - (bb[0] + bb[2]) / 2, c - (bb[1] + bb[3]) / 2 - s * 0.01), letter, font=font, fill=(255, 255, 255))
    # the spark (an electron on the orbit)
    ang = math.radians(-28)
    ex, ey = c + rx * math.cos(math.radians(-35)), c + ry * math.sin(math.radians(-35))
    px = c + (ex - c) * math.cos(ang) - (ey - c) * math.sin(ang)
    py = c + (ex - c) * math.sin(ang) + (ey - c) * math.cos(ang)
    g = int(s * 0.045)
    d.ellipse([px - g * 2, py - g * 2, px + g * 2, py + g * 2], fill=AMBER + (70,))
    d.ellipse([px - g, py - g, px + g, py + g], fill=AMBER)
    return img.resize((size, size), Image.LANCZOS)


def logo(name: str, out: Path) -> None:
    size = 800
    bg = Image.new("RGB", (size, size), DEEP)
    m = mark(int(size * 0.9), name[0].upper())
    bg.paste(m, ((size - m.width) // 2, (size - m.height) // 2), m)
    bg.save(out)


def banner(name: str, tagline: str, out: Path) -> None:
    w, h = 2560, 1440
    img = Image.new("RGB", (w, h), DEEP)
    px = ImageDraw.Draw(img)
    for y in range(h):  # soft vertical gradient
        f = y / h
        px.line([(0, y), (w, y)], fill=tuple(int(DEEP[i] + (NAVY[i] - DEEP[i]) * (1 - abs(f - 0.5) * 2)) for i in range(3)))
    # faint orbit rings for texture, far from the safe area
    ring = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    for k, rr in enumerate((520, 760, 1040)):
        rd.ellipse([w // 2 - rr * 2, h // 2 - rr, w // 2 + rr * 2, h // 2 + rr], outline=ICE + (18 - k * 4,), width=3)
    img = Image.alpha_composite(img.convert("RGBA"), ring)
    d = ImageDraw.Draw(img)
    big, small = ImageFont.truetype(FONT, 118), ImageFont.truetype(FONT_LIGHT, 52)
    text_w = max(d.textlength(name, font=big), d.textlength(tagline, font=small))
    emblem, gap = 280, 60
    total = emblem + gap + text_w
    if total > SAFE_W:  # YouTube only guarantees the centre 1546 px is visible on every device
        raise SystemExit(f"banner content is {total:.0f}px wide; must be <= {SAFE_W}. Use a shorter name or tagline.")
    x0 = (w - total) / 2
    m = mark(emblem, name[0].upper())
    img.alpha_composite(m, (int(x0), h // 2 - emblem // 2))
    tx = x0 + emblem + gap
    d.text((tx, h // 2 - 100), name, font=big, fill=(255, 255, 255))
    d.rectangle([tx, h // 2 + 50, tx + 130, h // 2 + 56], fill=AMBER)
    d.text((tx, h // 2 + 78), tagline, font=small, fill=ICE)
    img.convert("RGB").save(out, quality=92)


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "Brightwork Science"
    tagline = sys.argv[2] if len(sys.argv) > 2 else "How the world really works"
    out = Path("assets/brand")
    out.mkdir(parents=True, exist_ok=True)
    logo(name, out / "logo.png")
    banner(name, tagline, out / "banner.jpg")
    print("wrote", out / "logo.png", out / "banner.jpg")
