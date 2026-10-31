"""Animated data shots: a big counting number, growing bars, a timeline or a line chart, drawn in code (no model, no GPU) for the moment
the narrator gives the figures. Each shot is a short silent clip in the channel's navy-and-amber look.

The figures come from the narration itself: a model proposes a shot, and code throws it away unless every number in it appears in the
text, so a chart can never show something the narrator did not say."""
import re
import subprocess
import threading
from collections.abc import Callable
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT_BOLD = "/usr/share/fonts/truetype/lato/Lato-Bold.ttf"
FONT_BLACK = "/usr/share/fonts/truetype/lato/Lato-Black.ttf"
FONT_REG = "/usr/share/fonts/truetype/lato/Lato-Medium.ttf"
AMBER, ICE, WHITE, NAVY = (255, 190, 40), (190, 215, 255), (255, 255, 255), (14, 27, 61)
FPS = 24
KINDS = ("number", "bars", "timeline", "line")

PROMPT = """From this narrated section of a science video, pick AT MOST ONE moment where an animated data graphic would help the viewer
SEE the figures the narrator gives. Use ONLY numbers that appear in the narration, exactly as stated; never compute, convert or invent.

Kinds:
- "number": one striking figure, with its unit ("319", unit "Tb/s", label "record fibre speed")
- "bars": 2-5 values of the SAME unit to compare (temperatures, distances, sizes)
- "timeline": 3-6 dated events ("1911", "1933", ...), each with a label of at most 4 words
- "line": 3-8 (year, value) points of ONE quantity over time

Return JSON {{"shots": []}} when nothing fits (that is fine). Otherwise
{{"shots": [{{"kind": "number|bars|timeline|line", "title": str (<=6 words), "items": [{{"label": str, "value": number, "unit": str}}]}}]}}
For "timeline" give value = the year and unit = "". For "line" give label = the x value (year) and value = the figure.

SECTION: {heading}
NARRATION: {narration}"""

_font_cache: dict = {}


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def numbers_in(text: str) -> set[float]:
    """Every number written in a text ("3 000", "3,000", "44.7"), thousands separators removed."""
    cleaned = re.sub(r"(?<=\d)[,    ](?=\d{3}(?!\d))", "", text)
    out = set()
    for m in re.finditer(r"\d+(?:\.\d+)?", cleaned):
        out.add(float(m.group()))
    return out


def validate(shot: dict, narration: str) -> dict | None:
    """The shot if it is well formed and uses only numbers the narration states; else None."""
    if not isinstance(shot, dict) or shot.get("kind") not in KINDS:
        return None
    try:
        items = [{"label": str(i.get("label", ""))[:28], "value": float(i["value"]), "unit": str(i.get("unit", ""))[:14]}
                 for i in shot.get("items", [])]
    except (KeyError, TypeError, ValueError, AttributeError):
        return None
    need = {"number": (1, 1), "bars": (2, 5), "timeline": (3, 6), "line": (3, 8)}[shot["kind"]]
    if not need[0] <= len(items) <= need[1]:
        return None
    said = numbers_in(narration)
    xs = [float(re.sub(r"[^\d.]", "", i["label"]) or "nan") for i in items] if shot["kind"] == "line" else []
    if any(i["value"] not in said for i in items) or any(x not in said for x in xs):
        return None
    if shot["kind"] == "bars" and len({i["unit"] for i in items}) > 1:
        return None
    return {"kind": shot["kind"], "title": str(shot.get("title", ""))[:48], "items": items}


STOP = {"is", "are", "was", "were", "has", "have", "had", "its", "it", "the", "a", "an", "about", "only", "just", "over", "at", "of", "to", "by",
        "and", "in", "on", "that", "this", "with", "for", "from", "as", "roughly", "nearly", "almost", "around", "than", "up", "into"}
FIGURE_UNITS = {"km", "kilometres", "kilometers", "m", "metres", "meters", "cm", "mm", "miles", "kg", "tonnes", "tons", "years", "year", "seconds",
                "minutes", "hours", "days", "times", "percent", "%", "k", "kelvin", "°c", "°f", "degrees", "volts", "watts", "hz", "ghz", "mhz",
                "khz", "billion", "million", "thousand", "trillion", "tb/s", "gb/s", "mb/s", "km/h", "m/s", "g/cm³", "grams", "atm", "bar"}
_NUM_TOKEN = re.compile(r"^[\(\[“\"']*(\d[\d,]*(?:\.\d+)?)(%?)")


def rule_based_shot(narration: str) -> dict | None:
    """A plain "number" shot found without any model, for when the models are out of quota: the first figure that comes with a unit
    ("1,321 times", "142,976 km", "76 %"). The label is the words just before it. Less clever than the model's pick, but it means a
    busy day does not silently cost the video its graphic."""
    for sentence in re.split(r"(?<=[.!?])\s+", narration.strip()):
        words = sentence.split()
        for i, w in enumerate(words):
            m = _NUM_TOKEN.match(w)
            if not m:
                continue
            digits = m.group(1).replace(",", "")
            try:
                value = float(digits)
            except ValueError:
                continue
            unit = "%" if m.group(2) else ""
            if not unit and i + 1 < len(words):
                nxt = re.sub(r"[^\w%°/³]", "", words[i + 1]).lower()
                if nxt in FIGURE_UNITS:
                    unit = re.sub(r"[^\w%°/³]", "", words[i + 1])
            if not unit or (len(digits) == 4 and not unit and 1000 <= value <= 2100):
                continue
            before = [re.sub(r"[^\w'’-]", "", x) for x in words[max(0, i - 4):i]]
            label = " ".join(x.lower() for x in before if x and x.lower() not in STOP)[-24:].strip()
            shot = {"kind": "number", "title": (label or "By the numbers").capitalize()[:48],
                    "items": [{"label": label, "value": value, "unit": unit}]}
            return validate(shot, narration)
    return None


def propose_shot(heading: str, narration: str, gen: Callable[[str], dict]) -> tuple[dict | None, str]:
    """(shot or None, note about how it went). The model chooses; if the model is unavailable, a rule-based number shot is used instead."""
    try:
        out = gen(PROMPT.format(heading=heading, narration=narration))
    except Exception as exc:  # noqa: BLE001 - quota or outage: fall back to the rule-based shot
        shot = rule_based_shot(narration)
        return shot, f"model unavailable ({type(exc).__name__}); " + ("used a rule-based number shot" if shot else "no figure with a unit found")
    for s in (out.get("shots") if isinstance(out, dict) else None) or []:
        ok = validate(s, narration)
        if ok:
            return ok, "chosen by the model"
    return None, "the model found no figures worth drawing"


def extract_shot(heading: str, narration: str, gen: Callable[[str], dict]) -> dict | None:
    return propose_shot(heading, narration, gen)[0]


# ---------- drawing ----------
_bg_cache: dict = {}


def background(size: tuple[int, int]) -> Image.Image:
    if size not in _bg_cache:
        w, h = size
        y, x = np.mgrid[0:h, 0:w]
        d = np.clip(np.hypot((x - w / 2) / w, (y - h * 0.45) / h) / 0.75, 0, 1) ** 1.2
        top, bot = np.array((24, 46, 104)), np.array((6, 12, 34))
        arr = top[None, None, :] + (bot - top)[None, None, :] * d[..., None]
        img = Image.fromarray(arr.astype("uint8")).convert("RGBA")
        ring = Image.new("RGBA", size, (0, 0, 0, 0))
        rd = ImageDraw.Draw(ring)
        for r, a in ((0.55, 26), (0.8, 18), (1.05, 12)):
            rd.ellipse([w / 2 - w * r, h / 2 - h * r * 0.42, w / 2 + w * r, h / 2 + h * r * 0.42], outline=(214, 232, 255, a), width=3)
        img.alpha_composite(ring)
        _bg_cache[size] = img.convert("RGB")             # RGB, so ImageDraw's "RGBA" mode really blends translucent shapes
    return _bg_cache[size].copy()


def ease(t: float) -> float:
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** 3


def fmt(v: float, like: float) -> str:
    """A value counting up, written like the final one: whole numbers with separators, decimals with the same places."""
    places = len(str(like).split(".")[1]) if "." in str(like) and not float(like).is_integer() else 0
    return f"{v:,.{places}f}"


def text(d: ImageDraw.ImageDraw, xy, s: str, size: int, fill, path: str = FONT_BOLD, anchor: str = "la", alpha: float = 1.0) -> None:
    fill = tuple(fill[:3]) + (int(255 * max(0.0, min(1.0, alpha))),)
    d.text(xy, s, font=font(path, size), fill=fill, anchor=anchor)


def fit(s: str, path: str, size: int, width: int) -> int:
    """The largest font size (up to `size`) at which `s` fits `width`."""
    while size > 14 and font(path, size).getlength(s) > width:
        size -= 2
    return size


def rounded(d: ImageDraw.ImageDraw, box, r, fill) -> None:
    d.rounded_rectangle(box, radius=r, fill=fill)


def draw_title(d, size, title: str, t: float) -> None:
    w, h = size
    s = fit(title.upper(), FONT_BOLD, int(h * 0.04 if h < w else w * 0.045), int(w * 0.84))
    a = ease(t / 0.4)
    text(d, (w / 2, h * (0.14 if h < w else 0.13) - (1 - a) * 18), title.upper(), s, ICE, FONT_BOLD, "mm", a)
    bw = w * 0.1 * a
    d.rectangle([w / 2 - bw, h * (0.14 if h < w else 0.13) + s * 0.9, w / 2 + bw, h * (0.14 if h < w else 0.13) + s * 0.9 + 5], fill=AMBER + (255,))


def frame_number(shot, size, t) -> Image.Image:
    img = background(size)
    d = ImageDraw.Draw(img, "RGBA")
    w, h = size
    it = shot["items"][0]
    draw_title(d, size, shot["title"], t)
    k = ease((t - 0.35) / 1.9)
    value = fmt(it["value"] * k, it["value"])
    big = fit(fmt(it["value"], it["value"]), FONT_BLACK, int(min(w * 0.42, h * 0.30) if h < w else w * 0.34), int(w * 0.84))
    cx, cy = w / 2, h * (0.42 if h < w else 0.33)       # wide frames: everything stays above the caption band (the bottom quarter)
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([cx - w * 0.26, cy - h * 0.17, cx + w * 0.26, cy + h * 0.17], fill=AMBER + (int(70 * k),))
    img = Image.alpha_composite(img.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(min(w, h) * 0.07))).convert("RGB")
    d = ImageDraw.Draw(img, "RGBA")
    full_w = font(FONT_BLACK, big).getlength(fmt(it["value"], it["value"]))
    text(d, (cx - full_w / 2, cy), value, big, AMBER, FONT_BLACK, "lm", ease((t - 0.2) / 0.3))     # left-anchored: digits do not jitter
    if it["unit"]:
        text(d, (cx, cy + big * 0.72), it["unit"], int(big * 0.3), WHITE, FONT_BOLD, "mm", ease((t - 1.2) / 0.5))
    if it["label"]:
        text(d, (cx, cy + big * (1.12 if it["unit"] else 0.8)), it["label"], fit(it["label"], FONT_REG, int(big * 0.2), int(w * 0.8)), ICE,
             FONT_REG, "mm", ease((t - 1.6) / 0.5))
    return img


def frame_bars(shot, size, t) -> Image.Image:
    img = background(size)
    d = ImageDraw.Draw(img, "RGBA")
    w, h = size
    items = shot["items"]
    draw_title(d, size, shot["title"], t)
    top = h * (0.27 if h < w else 0.22)
    area = h * (0.56 if h < w else 0.36)
    row = area / len(items)
    left, right = (w * 0.2 if h < w else w * 0.3), w * 0.78                  # bars stop short of the edge: labels always fit outside
    vmax = max(i["value"] for i in items) or 1
    best = max(range(len(items)), key=lambda i: items[i]["value"])
    for n, it in enumerate(items):
        k = ease((t - 0.5 - 0.35 * n) / 1.4)
        y = top + n * row
        bar_h = row * 0.56
        text(d, (left - 20, y + bar_h / 2), it["label"], fit(it["label"], FONT_BOLD, int(bar_h * 0.55), int(left - 40)), WHITE, FONT_BOLD, "rm",
             ease((t - 0.4 - 0.35 * n) / 0.4))
        full = (right - left) * it["value"] / vmax
        rounded(d, (left, y, left + full, y + bar_h), int(bar_h / 2), (255, 255, 255, 22))
        if k > 0.01:
            col = AMBER if n == best else (96, 150, 235)
            rounded(d, (left, y, left + max(bar_h, full * k), y + bar_h), int(bar_h / 2), col + (255,))
        val = fmt(it["value"] * k, it["value"]) + (f" {it['unit']}" if it["unit"] else "")
        text(d, (left + max(bar_h, full * k) + 18, y + bar_h / 2), val, int(bar_h * 0.5), AMBER if n == best else WHITE, FONT_BLACK,
             "lm", ease((t - 0.7 - 0.35 * n) / 0.4))
    return img


def frame_timeline(shot, size, t) -> Image.Image:
    img = background(size)
    d = ImageDraw.Draw(img, "RGBA")
    w, h = size
    items = sorted(shot["items"], key=lambda i: i["value"])
    draw_title(d, size, shot["title"], t)
    n = len(items)
    prog = ease((t - 0.4) / (0.9 * n + 0.6))
    if h < w:                                                # horizontal, labels alternating above and below the line
        y0, x0, x1 = h * 0.56, w * 0.15, w * 0.85
        d.line([(x0, y0), (x0 + (x1 - x0) * prog, y0)], fill=ICE + (255,), width=6)
        for i, it in enumerate(items):
            x = x0 + (x1 - x0) * (i / max(1, n - 1))
            a = ease((t - 0.5 - 0.7 * i) / 0.5)
            if a <= 0.01:
                continue
            r = 14 + 6 * a
            d.ellipse([x - r, y0 - r, x + r, y0 + r], fill=AMBER + (255,))
            up = i % 2 == 0
            sgn = -1 if up else 1
            lab = it["label"]
            room = int(min((x1 - x0) / max(1, n - 1) * 1.8, 2 * min(x, w - x) - 20))       # keep the text inside the picture
            text(d, (x, y0 + sgn * h * 0.105 + (1 - a) * 12 * sgn), f"{int(it['value'])}", int(h * 0.075), AMBER, FONT_BLACK, "mm", a)
            text(d, (x, y0 + sgn * h * 0.185 + (1 - a) * 12 * sgn), lab, fit(lab, FONT_BOLD, int(h * 0.04), room), WHITE, FONT_BOLD, "mm", a)
    else:                                                    # vertical for Shorts: a line down the left, events to its right
        x0, y0, y1 = w * 0.2, h * 0.24, h * 0.58
        d.line([(x0, y0), (x0, y0 + (y1 - y0) * prog)], fill=ICE + (255,), width=7)
        for i, it in enumerate(items):
            y = y0 + (y1 - y0) * (i / max(1, n - 1))
            a = ease((t - 0.5 - 0.7 * i) / 0.5)
            if a <= 0.01:
                continue
            r = 16 + 7 * a
            d.ellipse([x0 - r, y - r, x0 + r, y + r], fill=AMBER + (255,))
            text(d, (x0 + 52 + (1 - a) * 30, y - 36), f"{int(it['value'])}", int(w * 0.085), AMBER, FONT_BLACK, "lm", a)
            text(d, (x0 + 52 + (1 - a) * 30, y + 50), it["label"], fit(it["label"], FONT_BOLD, int(w * 0.048), int(w * 0.66)), WHITE, FONT_BOLD, "lm", a)
    return img


def nice_ticks(lo: float, hi: float, n: int = 4) -> list[float]:
    span = (hi - lo) or 1.0
    raw = span / n
    mag = 10 ** np.floor(np.log10(raw))
    step = next(m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw)
    start = np.ceil(lo / step) * step
    return [float(v) for v in np.arange(start, hi + step * 0.01, step)]


def frame_line(shot, size, t) -> Image.Image:
    img = background(size)
    d = ImageDraw.Draw(img, "RGBA")
    w, h = size
    items = shot["items"]
    draw_title(d, size, shot["title"], t)
    xs = [float(re.sub(r"[^\d.]", "", i["label"])) for i in items]
    ys = [i["value"] for i in items]
    L, R = w * 0.14, w * 0.9
    T, B = (h * 0.3, h * 0.74) if h < w else (h * 0.24, h * 0.52)
    lo, hi = min(0.0, min(ys)), max(ys) * 1.08
    px = lambda x: L + (R - L) * (x - xs[0]) / ((xs[-1] - xs[0]) or 1)
    py = lambda y: B - (B - T) * (y - lo) / ((hi - lo) or 1)
    for tick in nice_ticks(lo, hi):
        gy = py(tick)
        d.line([(L, gy), (R, gy)], fill=(214, 232, 255, 30), width=2)
        text(d, (L - 14, gy), f"{tick:g}", int(h * 0.03), ICE, FONT_REG, "rm", ease((t - 0.3) / 0.4))
    prog = ease((t - 0.5) / 2.4) * (len(items) - 1)
    pts = [(px(x), py(y)) for x, y in zip(xs, ys, strict=True)]
    drawn = [pts[0]]
    for i in range(1, len(pts)):
        if prog >= i:
            drawn.append(pts[i])
        elif prog > i - 1:
            f = prog - (i - 1)
            drawn.append((pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * f, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * f))
    if len(drawn) > 1:
        d.line(drawn, fill=AMBER + (255,), width=8, joint="curve")
    for i, (x, y) in enumerate(pts):
        if prog >= i - 0.01:
            d.ellipse([x - 11, y - 11, x + 11, y + 11], fill=AMBER + (255,))
            text(d, (x, B + h * 0.045), items[i]["label"], int(h * 0.032), WHITE, FONT_BOLD, "mm", ease((prog - i + 0.5) / 0.5))
            text(d, (x, y - h * 0.045), fmt(items[i]["value"], items[i]["value"]) + items[i]["unit"], int(h * 0.036), WHITE, FONT_BLACK, "mm",
                 ease((prog - i + 0.5) / 0.5))
    return img


FRAMES = {"number": frame_number, "bars": frame_bars, "timeline": frame_timeline, "line": frame_line}
_lock = threading.Lock()


def render_shot(shot: dict, size: tuple[int, int], out: Path, seconds: float = 6.0, fps: int = FPS) -> Path:
    """The shot as a silent H.264 clip of exactly `seconds`; it holds its final picture for the last second or so."""
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{size[0]}x{size[1]}", "-r", str(fps), "-i", "-",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    draw = FRAMES[shot["kind"]]
    with _lock:
        for i in range(int(seconds * fps)):
            proc.stdin.write(draw(shot, size, i / fps).convert("RGB").tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise OSError("could not render the data shot")
    return out


def place_shot(shot: dict, sentences: list[dict], hold: float = 6.0) -> dict | None:
    """When to show a shot: from just before the narrator says its first figure. Returns {"start", "seconds"} (video seconds) or None."""
    first = shot["items"][0]
    target = first["value"] if shot["kind"] != "line" else float(re.sub(r"[^\d.]", "", first["label"]) or "nan")
    for s in sentences:
        for w in s.get("words") or []:
            if target in numbers_in(w["w"]):
                return {"start": round(max(s["start"], w["s"] - 0.4), 2), "seconds": hold}
    for s in sentences:
        if target in numbers_in(s["text"]):
            return {"start": round(s["start"], 2), "seconds": hold}
    return None


def shots_for(sections: list[dict], size: tuple[int, int], work: Path, gen: Callable[[str], dict] | None = None, min_gap: float = 10.0,
              render=None, log: Callable[[str], None] = print) -> list[dict]:
    """The data shots of a video: for each section ({"heading", "narration", "sentences"} with timed words) ask for a shot, check it against
    the narration, place it where the figure is spoken, and render its clip. Returns [{"start", "seconds", "clip", "kind"}], at least
    `min_gap` seconds apart. Any failure just means one shot fewer: a data shot is an extra and never stops a video."""
    from autopilot import llm

    gen = gen or llm.generate_json
    render = render or render_shot
    out: list[dict] = []
    for i, sec in enumerate(sections):
        try:
            shot, note = propose_shot(sec["heading"], sec["narration"], gen)
            when = place_shot(shot, sec["sentences"]) if shot else None
            if not (shot and when):
                log(f"[datashot] no shot for {sec['heading'][:40]!r}: " + (note if not shot else "could not find where the figure is spoken"))
                continue
            if out and when["start"] - out[-1]["start"] < min_gap:
                continue
            clip = render(shot, size, work / f"datashot_{i}.mp4", seconds=when["seconds"])
        except Exception as exc:  # noqa: BLE001
            log(f"[datashot] skipped one shot ({type(exc).__name__}: {exc})")
            continue
        log(f"[datashot] {shot['kind']} '{shot['title']}' at {when['start']:.1f}s ({note})")
        out.append({**when, "clip": clip, "kind": shot["kind"]})
    return out
