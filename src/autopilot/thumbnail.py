"""Thumbnail: best image from the video, darkened, with short bold text (1280x720)."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def thumbnail_text(script: dict) -> str:
    text = script.get("thumbnail_text") or script["title"].split(":")[0]
    return " ".join(text.split()[:5]).upper()


def _wrap(draw, text: str, font, max_width: int) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if cur and draw.textlength(trial, font=font) > max_width:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur]


def make_thumbnail(script: dict, background: Path | None, out: Path) -> Path:
    if background and background.exists():
        img = Image.open(background).convert("RGB")
        scale = max(W / img.width, H / img.height)
        img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
        left, top = (img.width - W) // 2, (img.height - H) // 2
        img = img.crop((left, top, left + W, top + H))
    else:
        img = Image.new("RGB", (W, H), (15, 25, 60))
    # left-to-right darkening keeps the text readable on any photo
    shade = Image.new("L", (W, 1))
    shade.putdata([int(200 * max(0.0, 1 - x / (W * 0.85))) for x in range(W)])
    shade = shade.resize((W, H))
    img = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), img, shade)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_BOLD, 120)
    lines = _wrap(draw, thumbnail_text(script), font, int(W * 0.62))
    y = (H - len(lines) * 130) // 2
    for line in lines:
        draw.text((60, y), line, font=font, fill=(255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0))
        y += 130
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, quality=90)  # YouTube limit is 2 MB; a 1280x720 JPEG is well under
    return out
