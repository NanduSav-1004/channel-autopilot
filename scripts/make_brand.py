"""Generate the channel logo (800x800) and banner (2560x1440) for a given name.

usage: python scripts/make_brand.py "Brightwork Science" "How the world really works"
       python scripts/make_brand.py "Brightwork Malayalam" "ലോകം എങ്ങനെ പ്രവർത്തിക്കുന്നു" --letter ബ --tag-font malayalam --out assets/brand_ml
Drawn at 4x and downsampled for clean edges. Banner text stays inside YouTube's 1546x423 safe area.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

NAVY, DEEP = (14, 27, 61), (7, 14, 36)
AMBER, ICE = (255, 183, 51), (214, 232, 255)
FONT = "/usr/share/fonts/truetype/lato/Lato-Bold.ttf"
FONT_LIGHT = "/usr/share/fonts/truetype/lato/Lato-Medium.ttf"
FONT_ML = "/usr/share/fonts/truetype/noto/NotoSansMalayalam-Regular.ttf"
FONT_ML_BOLD = "/usr/share/fonts/truetype/noto/NotoSansMalayalam-Bold.ttf"
SS = 4  # supersampling factor
SAFE_W = 1500  # banner content width limit (YouTube safe area is 1546 px)


def mark(size: int, letter: str, font_path: str = FONT) -> Image.Image:
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
    font = ImageFont.truetype(font_path, int(s * (0.46 if font_path == FONT_ML_BOLD else 0.52)))
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


def logo(name: str, out: Path, letter: str | None = None, font_path: str = FONT) -> None:
    size = 800
    bg = Image.new("RGB", (size, size), DEEP)
    m = mark(int(size * 0.9), letter or name[0].upper(), font_path)
    bg.paste(m, ((size - m.width) // 2, (size - m.height) // 2), m)
    bg.save(out)


def banner(name: str, tagline: str, out: Path, letter: str | None = None, tag_font: str = FONT_LIGHT,
           letter_font: str = FONT) -> None:
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
    emblem, gap = 280, 60
    for size in range(118, 70, -4):         # a longer name gets a slightly smaller type size instead of failing
        big, small = ImageFont.truetype(FONT, size), ImageFont.truetype(tag_font, round(size * 0.44))
        text_w = max(d.textlength(name, font=big), d.textlength(tagline, font=small))
        total = emblem + gap + text_w
        if total <= SAFE_W:
            break
    if total > SAFE_W:  # YouTube only guarantees the centre 1546 px is visible on every device
        raise SystemExit(f"banner content is {total:.0f}px wide; must be <= {SAFE_W}. Use a shorter name or tagline.")
    x0 = (w - total) / 2
    m = mark(emblem, letter or name[0].upper(), letter_font)
    img.alpha_composite(m, (int(x0), h // 2 - emblem // 2))
    tx = x0 + emblem + gap
    d.text((tx, h // 2 - 100), name, font=big, fill=(255, 255, 255))
    d.rectangle([tx, h // 2 + 50, tx + 130, h // 2 + 56], fill=AMBER)
    d.text((tx, h // 2 + 78), tagline, font=small, fill=ICE)
    img.convert("RGB").save(out, quality=92)


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("name", nargs="?", default="Brightwork Science")
    ap.add_argument("tagline", nargs="?", default="How the world really works")
    ap.add_argument("--letter", help="the emblem's letter (default: the name's first letter)")
    ap.add_argument("--tag-font", choices=["latin", "malayalam"], default="latin")
    ap.add_argument("--out", default="assets/brand")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    ml = a.tag_font == "malayalam"
    logo(a.name, out / "logo.png", a.letter, FONT_ML_BOLD if ml else FONT)
    banner(a.name, a.tagline, out / "banner.jpg", a.letter, FONT_ML if ml else FONT_LIGHT, FONT_ML_BOLD if ml else FONT)
    print("wrote", out / "logo.png", out / "banner.jpg")
