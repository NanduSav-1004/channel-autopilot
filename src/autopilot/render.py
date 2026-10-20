"""Render a long-form video: generated title cards + burned-in captions over narration (FFmpeg)."""
import colorsys
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1280, 720, 24
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _ass_time(t: float) -> str:
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def write_ass(timings: list[dict], path: Path) -> None:
    header = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1280\nPlayResY: 720\nWrapStyle: 0\n\n"
        "[V4+ Styles]\nFormat: Name,Fontname,Fontsize,PrimaryColour,OutlineColour,BackColour,Bold,"
        "BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV\n"
        "Style: Cap,Lato,40,&H00FFFFFF,&H00000000,&H80000000,1,1,3,0,2,90,90,70\n\n"
        "[Events]\nFormat: Layer,Start,End,Style,Text\n"
    )
    lines = []
    for sec in timings:
        for s in sec["sentences"]:
            text = s["text"].replace("\n", " ").replace("{", "(").replace("}", ")")
            lines.append(f"Dialogue: 0,{_ass_time(s['start'])},{_ass_time(s['end'])},Cap,{text}")
    path.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")


def make_card(title: str, heading: str, idx: int, total: int, path: Path) -> None:
    hue = (0.58 + 0.07 * idx) % 1.0
    top = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(hue, 0.65, 0.35))
    bottom = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(hue, 0.8, 0.12))
    img = Image.new("RGB", (W, H))
    px = ImageDraw.Draw(img)
    for y in range(H):
        f = y / H
        px.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * f) for i in range(3)))
    d = ImageDraw.Draw(img)
    big, small = ImageFont.truetype(FONT_BOLD, 64), ImageFont.truetype(FONT_BOLD, 24)
    d.text((80, 70), title.upper()[:60], font=small, fill=(255, 255, 255, 160))
    words, lines, cur = heading.split(), [], ""
    for w in words:
        if len(cur) + len(w) > 26:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    lines.append(cur)
    y = 190
    for ln in lines[:3]:
        d.text((80, y), ln, font=big, fill=(255, 255, 255))
        y += 82
    bar_w = int((W - 160) * (idx + 1) / total)
    d.rectangle([80, H - 30, W - 80, H - 24], fill=(255, 255, 255, 40))
    d.rectangle([80, H - 30, 80 + bar_w, H - 24], fill=(255, 255, 255))
    img.save(path)


def render_video(script: dict, timings: list[dict], narration: Path, out_mp4: Path, work: Path) -> None:
    work.mkdir(parents=True, exist_ok=True)
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    concat = []
    for i, sec in enumerate(timings):
        card = work / f"card_{i:02d}.png"
        make_card(script["title"], sec["heading"], i, len(timings), card)
        concat.append(f"file '{card.name}'\nduration {sec['end'] - sec['start']:.3f}")
    concat.append(f"file 'card_{len(timings) - 1:02d}.png'")  # concat demuxer quirk: repeat last frame
    (work / "cards.txt").write_text("\n".join(concat) + "\n")
    write_ass(timings, work / "captions.ass")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(work / "cards.txt"),
         "-i", str(narration), "-vf", f"fps={FPS},ass={work / 'captions.ass'},format=yuv420p",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-tune", "stillimage",
         "-c:a", "aac", "-b:a", "128k", "-shortest", str(out_mp4)],
        check=True, capture_output=True,
    )


def _prep_image(src: Path, dst: Path) -> None:
    """Cover-fit to 1920x1080 so zoompan has headroom and smooth motion."""
    img = Image.open(src).convert("RGB")
    scale = max(1920 / img.width, 1080 / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    left, top = (img.width - 1920) // 2, (img.height - 1080) // 2
    img.crop((left, top, left + 1920, top + 1080)).save(dst, quality=92)


def _motion(idx: int, n: int) -> tuple[str, str, str]:
    """Rotate Ken Burns variants so consecutive shots don't repeat the same move."""
    centre_x, centre_y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    variant = idx % 3
    if variant == 0:
        return f"1+0.12*on/{n}", centre_x, centre_y          # slow zoom in
    if variant == 1:
        return f"1.12-0.12*on/{n}", centre_x, centre_y       # slow zoom out
    return "1.12", f"(iw-iw/zoom)*on/{n}", centre_y          # pan left to right


def _render_clip(img: Path, frames: int, idx: int, out: Path) -> None:
    z, x, y = _motion(idx, frames)
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(img), "-vf",
         f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={FPS},format=yuv420p",
         "-frames:v", str(frames), "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", str(out)],
        check=True, capture_output=True,
    )


def _render_stock_clip(src: Path, frames: int, out: Path) -> None:
    """Loop/trim a stock clip to the shot length, cover-crop to 16:9, strip its audio."""
    subprocess.run(
        ["ffmpeg", "-y", "-stream_loop", "-1", "-i", str(src), "-an", "-vf",
         f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},format=yuv420p",
         "-frames:v", str(frames), "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", str(out)],
        check=True, capture_output=True,
    )


def render_photo_video(script, timings, images, plan, narration: Path, out_mp4: Path, work: Path) -> None:
    """Ken Burns over gathered images; sections without images fall back to title cards."""
    from concurrent.futures import ThreadPoolExecutor

    work.mkdir(parents=True, exist_ok=True)
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    jobs = []
    for si, (sec, spans) in enumerate(zip(timings, plan)):
        pool = images[si]
        for ji, (a, b) in enumerate(spans):
            n, out = len(jobs), work / f"clip_{len(jobs):04d}.mp4"
            item = pool[ji % len(pool)] if pool else None
            if item and item["kind"] == "video":
                jobs.append(("video", item["path"], b - a, n, out))
                continue
            src = item["path"] if item else work / f"card_{si:02d}.png"
            if not item:
                make_card(script["title"], sec["heading"], si, len(timings), src)
            prepped = work / f"prep_{n:04d}.jpg"
            _prep_image(src, prepped)
            jobs.append(("image", prepped, b - a, n, out))

    def run(job):
        kind, src, frames, n, out = job
        _render_stock_clip(src, frames, out) if kind == "video" else _render_clip(src, frames, n, out)

    with ThreadPoolExecutor(max_workers=2) as ex:
        list(ex.map(run, jobs))
    (work / "clips.txt").write_text("".join(f"file '{j[4].name}'\n" for j in jobs))
    write_ass(timings, work / "captions.ass")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(work / "clips.txt"),
         "-i", str(narration), "-vf", f"ass={work / 'captions.ass'}",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "128k", "-shortest", str(out_mp4)],
        check=True, capture_output=True,
    )
