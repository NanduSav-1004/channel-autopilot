"""Thumbnail (1280x720): the most striking image from the video, graded for punch, with a heavy headline whose key
word is amber, a tag from the video's style, and a small brand badge."""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

W, H = 1280, 720
FONT_HEAVY = "/usr/share/fonts/truetype/lato/Lato-Black.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/lato/Lato-Bold.ttf"
FONT_FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_ML = "/usr/share/fonts/truetype/noto/NotoSansMalayalam-Bold.ttf"
_lang = {"fonts": None}   # set for the duration of one make_thumbnail call (e.g. Malayalam script)
AMBER, NAVY, INK = (255, 190, 40), (14, 27, 61), (6, 10, 30)
SERIES_TAG = {
    "how_it_works": "HOW IT WORKS", "myth_vs_reality": "MYTH OR FACT?", "origin_story": "THE ORIGIN STORY",
    "scale_and_numbers": "BY THE NUMBERS", "what_if": "WHAT IF?",
}
SERIES_TAG_ML = {
    "how_it_works": "എങ്ങനെ പ്രവർത്തിക്കുന്നു", "myth_vs_reality": "മിഥ്യയോ സത്യമോ?", "origin_story": "കണ്ടെത്തലിന്റെ കഥ",
    "scale_and_numbers": "കണക്കുകളിൽ", "what_if": "എങ്കിൽ എന്ത് സംഭവിക്കും?",
}


def _font(size: int, heavy: bool = True, latin: bool = False) -> ImageFont.FreeTypeFont:
    for path in (*(() if latin else _lang["fonts"] or ()), FONT_HEAVY if heavy else FONT_BOLD, FONT_BOLD, FONT_FALLBACK):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _is_latin(ch: str) -> bool:
    return ch.isascii() and not ch.isspace()


def _runs(text: str) -> list[tuple[str, bool]]:
    """Split text into runs of Latin (ASCII) and other letters: the Malayalam font has no Latin glyphs, so "CPU" inside a
    Malayalam headline vanished. Spaces stay with the run before them."""
    runs: list[list] = []
    for ch in text:
        latin = _is_latin(ch) if not ch.isspace() else (runs[-1][1] if runs else False)
        if runs and runs[-1][1] == latin:
            runs[-1][0] += ch
        else:
            runs.append([ch, latin])
    return [(s, lat) for s, lat in runs]


def _width(draw: ImageDraw.ImageDraw, text: str, size: int, heavy: bool = True) -> float:
    if not _lang["fonts"]:
        return draw.textlength(text, font=_font(size, heavy))
    return sum(draw.textlength(s, font=_font(size, heavy, latin=lat)) for s, lat in _runs(text))


def _draw_text(draw: ImageDraw.ImageDraw, xy: tuple[float, float], text: str, size: int, heavy: bool = True, **kw) -> None:
    """Draw text; on a Malayalam thumbnail each script gets a font that has its letters, sharing one baseline."""
    if not _lang["fonts"]:
        draw.text(xy, text, font=_font(size, heavy), **kw)
        return
    x, base = xy[0], xy[1] + size * 0.86
    for seg, lat in _runs(text):
        font = _font(size, heavy, latin=lat)
        draw.text((x, base), seg, font=font, anchor="ls", **kw)
        x += draw.textlength(seg, font=font)


def thumbnail_text(script: dict) -> str:
    text = script.get("thumbnail_text") or script["title"].split(":")[0]
    return " ".join(text.split()[:5]).upper()


def colorfulness(img: Image.Image) -> float:
    """Hasler-Susstrunk colourfulness: about 0 for greyscale, 40+ for vivid."""
    a = np.asarray(img.convert("RGB").resize((320, 180))).astype(float)
    rg, yb = a[..., 0] - a[..., 1], 0.5 * (a[..., 0] + a[..., 1]) - a[..., 2]
    return math.hypot(rg.std(), yb.std()) + 0.3 * math.hypot(rg.mean(), yb.mean())


def visual_interest(img: Image.Image) -> float:
    """How eye-catching an image is likely to be: colour, contrast and detail, minus mostly-white or mostly-black."""
    gray = np.asarray(img.convert("L").resize((320, 180))).astype(float)
    score = colorfulness(img) + 0.5 * gray.std() + 3.0 * np.abs(np.diff(gray, axis=1)).mean()
    if gray.mean() > 205:      # a white page or diagram
        score -= 25
    if gray.mean() < 30:       # nearly black
        score -= 25
    return score


def pick_background(paths: list[Path]) -> Path | None:
    """The most striking usable image: landscape, big enough, scored by visual_interest."""
    best, best_score = None, -1e9
    for p in paths:
        try:
            with Image.open(p) as im:
                if im.width < 900 or im.width / im.height < 1.2:
                    continue
                score = visual_interest(im)
        except OSError:
            continue
        if score > best_score:
            best, best_score = p, score
    return best


PICK_PROMPT = """Choose the best background image for the YouTube thumbnail of a video titled "{title}".
The {n} candidates are attached, numbered 1 to {n} in order.
Prefer: clearly related to the topic, visually striking (strong colour or contrast, one clear subject), simple.
Reject images with lots of text, logos, watermarks, maps, charts, tables or screenshots, and murky or cluttered ones.
Return JSON: {{"best": <number 1-{n}>, "reason": str}}"""


def _small_jpeg(path: Path, side: int = 512) -> bytes:
    import io

    img = Image.open(path).convert("RGB")
    img.thumbnail((side, side))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=70)
    return buf.getvalue()


def shortlist(paths: list[Path], k: int = 8) -> list[Path]:
    """The k most visually interesting usable images (the vision model chooses among these)."""
    scored = []
    for p in paths:
        try:
            with Image.open(p) as im:
                if im.width < 900 or im.width / im.height < 1.2:
                    continue
                scored.append((visual_interest(im), str(p), p))
        except OSError:
            continue
    return [p for _, _, p in sorted(scored, reverse=True)[:k]]


def pick_with_vision(script: dict, paths: list[Path], gen=None) -> Path | None:
    """Ask the vision model which shortlisted image makes the best thumbnail (on topic, striking, no text/charts).
    Any failure falls back to the colour-and-contrast pick."""
    from autopilot import llm

    gen = gen or llm.generate_json
    short = shortlist(paths)
    if len(short) < 2:
        return pick_background(paths)
    try:
        best = int(gen(PICK_PROMPT.format(title=script["title"], n=len(short)), images=[_small_jpeg(p) for p in short])["best"])
        if 1 <= best <= len(short):
            return short[best - 1]
    except (llm.LLMError, KeyError, TypeError, ValueError, OSError):
        pass
    return short[0]


def grade(img: Image.Image) -> Image.Image:
    """Punchy colour. Dull or black-and-white images become a navy-to-amber duotone so they look deliberate."""
    img = img.convert("RGB")
    if colorfulness(img) < 14:
        gray = ImageOps.autocontrast(img.convert("L"), cutoff=1)
        img = ImageOps.colorize(gray, black=(8, 14, 40), mid=(150, 70, 70), white=(255, 215, 130), midpoint=120)
    img = ImageEnhance.Contrast(img).enhance(1.18)
    img = ImageEnhance.Color(img).enhance(1.35)
    return ImageEnhance.Sharpness(img).enhance(1.4)


def _cover(img: Image.Image, focus_x: float = 0.7) -> Image.Image:
    """Fill 1280x720, keeping the right side (where the subject should be) rather than the centre; text sits left."""
    s = max(W / img.width, H / img.height) * 1.04
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    left = round((img.width - W) * focus_x)
    top = (img.height - H) // 2
    return img.crop((left, top, left + W, top + H))


def _overlay(img: Image.Image) -> Image.Image:
    """A dark-to-clear gradient behind the headline (left) and a soft vignette, so text is readable on any photo."""
    x = np.linspace(0, 1, W)[None, :]
    y = np.linspace(-1, 1, H)[:, None]
    left = np.clip(1 - x / 0.62, 0, 1) ** 1.3 * 0.78
    vignette = np.clip((np.abs(y) - 0.55) / 0.45, 0, 1) * 0.45
    alpha = np.clip(left + vignette, 0, 0.9)
    shade = Image.new("RGBA", (W, H), INK + (0,))
    shade.putalpha(Image.fromarray((alpha * 255).astype("uint8")))
    return Image.alpha_composite(img.convert("RGBA"), shade)


def _splits(words: list[str]) -> list[list[str]]:
    """Candidate ways to break the headline into 1-3 lines, most balanced first."""
    n = len(words)
    options = [[" ".join(words)]]
    if n >= 2:
        for cut in range(1, n):
            options.append([" ".join(words[:cut]), " ".join(words[cut:])])
    if n >= 3:
        for a in range(1, n - 1):
            for b in range(a + 1, n):
                options.append([" ".join(words[:a]), " ".join(words[a:b]), " ".join(words[b:])])
    return options


def _fit(text: str, draw: ImageDraw.ImageDraw, max_w: int, max_h: int) -> tuple[list[str], int]:
    """The line breaks and font size that make the headline as BIG as the space allows."""
    best_lines, best_size = [text], 40
    for lines in _splits(text.split()):
        size = 240
        while size > 40:
            if max(_width(draw, line, size) for line in lines) <= max_w and len(lines) * size * 1.0 <= max_h:
                break
            size -= 4
        if size > best_size:
            best_lines, best_size = lines, size
    return best_lines, best_size


def key_word(text: str) -> str:
    """The word to highlight: the last one if it is substantial, otherwise the longest."""
    words = [w for w in text.split() if any(c.isalnum() for c in w)]
    if not words:
        return ""
    return words[-1] if len(words[-1].strip("?!.,")) >= 4 else max(words, key=lambda w: len(w.strip("?!.,")))


def _draw_headline(canvas: Image.Image, text: str) -> None:
    draw = ImageDraw.Draw(canvas)
    hi = key_word(text)
    lines, size = _fit(text, draw, int(W * 0.64), int(H * 0.70))
    stroke = max(7, size // 14)
    line_h = int(size * 1.0)
    y = (H - len(lines) * line_h) // 2 + 12
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    marked = False
    placed = []
    for line in lines:
        x, parts = 58, []
        for word in line.split(" "):
            is_hi = (word == hi) and not marked
            marked = marked or is_hi
            parts.append((word, x, is_hi))
            x += _width(draw, word + " ", size)
        placed.append((y, parts))
        y += line_h
    for ly, parts in placed:                                   # drop shadow first, blurred
        for word, wx, _ in parts:
            _draw_text(sd, (wx + 7, ly + 9), word, size, fill=(0, 0, 0, 200), stroke_width=stroke, stroke_fill=(0, 0, 0, 200))
    canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(5)))
    draw = ImageDraw.Draw(canvas)
    for ly, parts in placed:
        for word, wx, is_hi in parts:
            _draw_text(draw, (wx, ly), word, size, fill=AMBER if is_hi else (255, 255, 255),
                      stroke_width=stroke, stroke_fill=(10, 12, 24))


def _draw_tag(canvas: Image.Image, label: str) -> None:
    draw = ImageDraw.Draw(canvas)
    tw = _width(draw, label, 44)
    box = (48, 40, 48 + tw + 52, 40 + 70)
    draw.rounded_rectangle(box, radius=14, fill=AMBER)
    _draw_text(draw, (48 + 26, 40 + 8), label, 44, fill=INK)


def _draw_badge(canvas: Image.Image) -> None:
    """Brand badge in the top-right; the bottom-right is where YouTube overlays the video length."""
    d = ImageDraw.Draw(canvas)
    cx, cy, r = W - 96, 92, 56
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=NAVY, outline=AMBER, width=7)
    font = _font(72, latin=True)   # the badge letter is Latin even on a Malayalam thumbnail
    bb = d.textbbox((0, 0), "B", font=font)
    d.text((cx - (bb[0] + bb[2]) / 2, cy - (bb[1] + bb[3]) / 2 - 3), "B", font=font, fill=(255, 255, 255))


def make_thumbnail(script: dict, background: "Path | list[Path] | None", out: Path, pick=None, lang: str = "en") -> Path:
    """`pick(script, paths)` chooses the image (the pipeline passes pick_with_vision); default is the colour score."""
    _lang["fonts"] = (FONT_ML,) if lang == "ml" else None
    try:
        return _make(script, background, out, pick, lang)
    finally:
        _lang["fonts"] = None


def _make(script: dict, background, out: Path, pick, lang: str) -> Path:
    paths = [background] if isinstance(background, Path) else list(background or [])
    paths = [Path(p) for p in paths if p and Path(p).exists()]
    chosen = pick(script, paths) if pick else pick_background(paths)
    if chosen:
        base = _cover(grade(Image.open(chosen)))
    else:
        base = Image.new("RGB", (W, H), NAVY)
    canvas = _overlay(base)
    _draw_headline(canvas, thumbnail_text(script))
    tags, default = (SERIES_TAG_ML, "വിശദീകരണം") if lang == "ml" else (SERIES_TAG, "EXPLAINED")
    _draw_tag(canvas, tags.get(script.get("series", ""), default))
    _draw_badge(canvas)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(out, quality=90)  # YouTube limit is 2 MB; a 1280x720 JPEG is well under
    return out
