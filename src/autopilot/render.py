"""Render a long-form video: generated title cards + burned-in captions over narration (FFmpeg)."""
import colorsys
import itertools
import shutil
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
        "Style: Cap,Lato,40,&H00FFFFFF,&HA0000000,&HA0000000,1,3,9,0,2,90,90,60\n\n"
        "[Events]\nFormat: Layer,Start,End,Style,Text\n"
    )
    lines = []
    for sec in timings:
        for s in sec["sentences"]:
            text = s["text"].replace("\n", " ").replace("{", "(").replace("}", ")")
            lines.append(f"Dialogue: 0,{_ass_time(s['start'])},{_ass_time(s['end'])},Cap,{text}")
    path.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")


HILITE = "&H0033B7FF"  # the brand amber, in ASS's BGR order


# Caption looks. `group` = words shown at once; the word being spoken is highlighted.
SHORT_CAPTIONS = {"res": (1080, 1920), "font": 96, "margin_v": 600, "group": 4, "upper": True, "outline": 10}
LONG_CAPTIONS = {"res": (1280, 720), "font": 52, "margin_v": 50, "group": 7, "upper": False, "outline": 5}
FONT_CAPTION = "/usr/share/fonts/truetype/lato/Lato-Bold.ttf"


def make_fits(look: dict):
    """A function telling whether a phrase fits the screen width at the caption font size, measured with the real
    font (so uppercase and wide letters are accounted for). Falls back to a character budget if the font is missing."""
    w = look["res"][0]
    limit = w - 2 * round(w * 0.06) - 2 * look["outline"]
    try:
        font = ImageFont.truetype(look.get("font_path", FONT_CAPTION), look["font"])
    except OSError:
        budget = int(limit / (look["font"] * (0.66 if look["upper"] else 0.56)))
        return lambda words: len(" ".join(words)) <= budget

    def fits(words: list[str]) -> bool:
        text = " ".join(words)
        return font.getlength(text.upper() if look["upper"] else text) <= limit

    return fits


def caption_groups(words: list[dict], group: int, fits=None) -> list[list[dict]]:
    """Split a sentence's words into on-screen phrases: at most `group` words, never wider than the screen (`fits`),
    breaking at sentence ends and after a comma once there are two words, and not leaving a lone word at the end."""
    chunks, cur = [], []
    for w in words:
        if cur and fits and not fits([x["w"] for x in cur] + [w["w"]]):
            chunks.append(cur)
            cur = []
        cur.append(w)
        last = w["w"][-1]
        if len(cur) >= group or last in ".!?" or (last in ",;:" and len(cur) >= 2):
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    if (len(chunks) > 1 and len(chunks[-1]) == 1 and len(chunks[-2]) <= group
            and (not fits or fits([x["w"] for x in chunks[-2] + chunks[-1]]))):  # never leave a lone last word
        lone = chunks.pop()          # pop first: `chunks[-2] += chunks.pop()` assigns into the wrong slot
        chunks[-1] += lone
    return chunks


def write_ass_words(timings: list[dict], path: Path, look: dict) -> None:
    """Word-by-word captions: a short phrase on screen, the word being spoken in amber. One ASS event per word, so
    the highlight moves exactly with the voice."""
    from autopilot.tts import estimate_word_times

    w, h = look["res"]
    header = (
        f"[Script Info]\nScriptType: v4.00+\nPlayResX: {w}\nPlayResY: {h}\nWrapStyle: 0\n\n"
        "[V4+ Styles]\nFormat: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,"
        "BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV\n"
        f"Style: Cap,{look.get('fontname', 'Lato')},{look['font']},&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,1,1,{look['outline']},3,2,"
        f"{round(w * 0.06)},{round(w * 0.06)},{look['margin_v']}\n\n"
        "[Events]\nFormat: Layer,Start,End,Style,Text\n"
    )

    fits = make_fits(look)

    def clean(word: str) -> str:
        word = word.replace("{", "(").replace("}", ")").replace("\\", "")
        return word.upper() if look["upper"] else word

    events = []  # (start, end, text)
    for sec in timings:
        for sent in sec["sentences"]:
            words = sent.get("words") or estimate_word_times(sent["text"], sent["start"], sent["end"])
            for chunk in caption_groups(words, look["group"], fits):
                for j, cur in enumerate(chunk):
                    end = chunk[j + 1]["s"] if j + 1 < len(chunk) else min(cur["e"] + 0.25, sent["end"] + 0.25)
                    text = " ".join(
                        (f"{{\\c{HILITE}&}}{clean(x['w'])}{{\\r}}" if k == j else clean(x["w"])) for k, x in enumerate(chunk))
                    events.append([cur["s"], end, text])
    for ev, nxt in itertools.pairwise(events):  # a phrase lingers a moment, but never into the next one
        ev[1] = min(ev[1], nxt[0])
    lines = [f"Dialogue: 0,{_ass_time(s)},{_ass_time(max(e, s + 0.04))},Cap,{text}" for s, e, text in events]
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


def _motion(variant: int, n: int, cycle: int = 0) -> tuple[str, str, str]:
    """The camera move for a shot. First use of an image: a slow zoom or pan over the whole picture (variants rotate so
    neighbours differ). A repeat (cycle 1, 2) looks at a DIFFERENT PART: a pan across the top, then across the bottom,
    at a fixed high zoom, so a re-used image reads as a new shot."""
    if cycle == 1:
        return "1.4", f"(iw-iw/zoom)*on/{n}", "(ih-ih/zoom)*0.12"          # pan left to right along the top
    if cycle >= 2:
        return "1.4", f"(iw-iw/zoom)*(1-on/{n})", "(ih-ih/zoom)*0.88"      # pan right to left along the bottom
    centre_x, centre_y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    variant = variant % 3
    if variant == 0:
        return f"1+0.12*on/{n}", centre_x, centre_y          # slow zoom in
    if variant == 1:
        return f"1.12-0.12*on/{n}", centre_x, centre_y       # slow zoom out
    return "1.12", f"(iw-iw/zoom)*on/{n}", centre_y          # pan left to right


def _render_clip(img: Path, frames: int, variant: int, out: Path, cycle: int = 0) -> None:
    z, x, y = _motion(variant, frames, cycle)
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(img), "-vf",
         f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={FPS},format=yuv420p",
         "-frames:v", str(frames), "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", str(out)],
        check=True, capture_output=True,
    )


def _render_stock_clip(src: Path, frames: int, out: Path, offset: float = 0.0) -> None:
    """Loop/trim a stock clip to the shot length, cover-crop to 16:9, strip its audio. `offset` starts a re-used
    clip from a different point so the second appearance does not look like a repeat."""
    subprocess.run(
        ["ffmpeg", "-y", "-ss", f"{offset:.2f}", "-stream_loop", "-1", "-i", str(src), "-an", "-vf",
         f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},format=yuv420p",
         "-frames:v", str(frames), "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", str(out)],
        check=True, capture_output=True,
    )


def render_photo_video(
    script, timings, images, plan, narration: Path, out_mp4: Path, work: Path, music: Path | None = None,
    look: dict = LONG_CAPTIONS, mascot: str | None = None,
) -> None:
    """Ken Burns over gathered images; sections without images fall back to title cards."""
    from concurrent.futures import ThreadPoolExecutor

    work.mkdir(parents=True, exist_ok=True)
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    from autopilot.shots import cut_choice

    jobs = []
    for si, (sec, spans) in enumerate(zip(timings, plan, strict=True)):
        pool = images[si]
        for ji, (a, b) in enumerate(spans):
            out = work / f"clip_{len(jobs):04d}.mp4"
            item_idx, cycle, variant = cut_choice(ji, len(pool)) if pool else (0, 0, ji)
            item = pool[item_idx] if pool else None
            if item and item.get("borrowed"):  # shown in another section already: use a different part of it here
                cycle = min(cycle + 1, 2)
            if item and item["kind"] == "video":
                jobs.append(("video", item["path"], b - a, 2.0 * cycle, out))
                continue
            src = item["path"] if item else work / f"card_{si:02d}.png"
            if not item:
                make_card(script["title"], sec["heading"], si, len(timings), src)
            prepped = work / f"prep_{item_idx if pool else 'c'}_{si}.jpg"
            if not prepped.exists():
                _prep_image(src, prepped)
            jobs.append(("image", prepped, b - a, (variant, cycle), out))

    def run(job):
        kind, src, frames, extra, out = job
        if kind == "video":
            _render_stock_clip(src, frames, out, extra)
        else:
            _render_clip(src, frames, extra[0], out, extra[1])

    with ThreadPoolExecutor(max_workers=2) as ex:
        list(ex.map(run, jobs))
    (work / "clips.txt").write_text("".join(f"file '{j[4].name}'\n" for j in jobs))
    write_ass_words(timings, work / "captions.ass", look)
    _final_pass(work / "clips.txt", narration, work / "captions.ass", out_mp4, music,
                _mascot(narration, work, vertical=False, style=mascot) if mascot else None)


# Voice to -16 LUFS; the music bed to -21 LUFS, then ducked hard by sidechain compression while the narrator speaks.
# Measured: that keeps the bed ~20-24 dB under the voice during speech, the balance of the original (liked) mix.
VOICE_LUFS, MUSIC_LUFS = -16, -21
VOICE_NORM = f"loudnorm=I={VOICE_LUFS}:TP=-1.5:LRA=7"
GRAPH_DUCKED = (
    f"[0:a]{VOICE_NORM},asplit=2[nar][sc];"
    f"[1:a]loudnorm=I={MUSIC_LUFS}:TP=-3:LRA=11,lowpass=f=3000[mus];"
    "[mus][sc]sidechaincompress=threshold=0.02:ratio=10:attack=30:release=600[duck];"
    "[nar][duck]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]"
)
GRAPH_STEADY = (  # simpler fallback: the music at a fixed low level, no ducking
    f"[0:a]{VOICE_NORM}[nar];[1:a]loudnorm=I=-28:TP=-3:LRA=11,lowpass=f=3000[mus];"
    "[nar][mus]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]"
)
SPEECH_FLOOR_DB, LOSS_TOLERANCE_DB = -32.0, 3.0


def _envelope(path: Path, win: float = 0.5):
    """Loudness (dBFS) of an audio file in `win`-second windows."""
    import numpy as np

    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype="<i2").astype(float) / 32768
    n = int(16000 * win)
    return np.array([20 * np.log10(np.sqrt((x[i:i + n] ** 2).mean()) + 1e-9) for i in range(0, max(0, len(x) - n), n)])


def voice_losses(ref_wav: Path, mixed_wav: Path, win: float = 0.5) -> list[float]:
    """Times (seconds) where the narrator is speaking in `ref_wav` but the mix is more than LOSS_TOLERANCE_DB quieter:
    the voice has been lost. (A correct mix is never quieter than the voice alone: it only adds music.)"""
    ref, mix = _envelope(ref_wav, win), _envelope(mixed_wav, win)
    return [round(i * win, 1) for i, (r, m) in enumerate(zip(ref, mix, strict=False))
            if r > SPEECH_FLOOR_DB and m < r - LOSS_TOLERANCE_DB]


def mix_audio(narration: Path, music: Path | None, out_wav: Path) -> str:
    """Mix narration and music into `out_wav` (48 kHz) in an audio-only pass, and VERIFY the voice survived.
    Mixing inside the video encode was found to drop the voice at random moments, so the audio is built on its own,
    checked against the voice alone, and falls back to a simpler mix, then to the voice alone, if it is not clean."""
    import wave

    with wave.open(str(narration)) as w:
        dur = w.getnframes() / w.getframerate()
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    ref = out_wav.with_suffix(".voice.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(narration), "-af", VOICE_NORM, "-ar", "48000", "-ac", "1",
                    str(ref)], check=True)
    if music:
        for label, graph in (("music ducked", GRAPH_DUCKED), ("music steady", GRAPH_STEADY)):
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(narration), "-stream_loop", "-1", "-i", str(music),
                            "-filter_complex", graph, "-map", "[a]", "-t", f"{dur:.3f}", "-ar", "48000", "-ac", "1",
                            str(out_wav)], check=True)
            lost = voice_losses(ref, out_wav)
            if not lost:
                return label
            print(f"[mix] WARNING: '{label}' lost the voice at {lost[:6]} s; trying a simpler mix", flush=True)
        print("[mix] WARNING: dropping the music: every mix lost the voice", flush=True)
    shutil.copy(ref, out_wav)
    return "voice only"


def _final_pass(clips: Path, narration: Path, ass: Path, out_mp4: Path, music: Path | None,
                mascot: tuple[Path, int, int] | None = None) -> None:
    """Burn captions into the video and attach the pre-mixed, verified audio. `mascot` = (transparent video, x, y): the talking
    character is overlaid at that position."""
    mixed = out_mp4.with_suffix(".mix.wav")
    how = mix_audio(narration, music, mixed)
    print(f"[mix] audio: {how}", flush=True)
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(clips), "-i", str(mixed)]
    if mascot:
        track, x, y = mascot
        cmd += ["-i", str(track), "-filter_complex",
                f"[0:v]ass={ass}[v];[v][2:v]overlay={x}:{y}:eof_action=pass,format=yuv420p[out]", "-map", "[out]"]
    else:
        cmd += ["-vf", f"ass={ass}", "-map", "0:v"]
    cmd += ["-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", str(out_mp4)]
    subprocess.run(cmd, check=True, capture_output=True)


def _mascot(narration: Path, work: Path, vertical: bool, style: str) -> tuple[Path, int, int] | None:
    """The talking mascot's track and where it sits: bottom-left, clear of the captions and of YouTube's own buttons.
    The mascot is an extra: if anything about it fails, the video is rendered without it rather than not at all."""
    try:
        from autopilot import mascot

        size = 300 if vertical else 230
        track = mascot.render_track(narration, work / "mascot.mov", size=size, style=style)
        return (track, 24, 1380) if vertical else (track, 18, 396)
    except Exception as exc:  # noqa: BLE001
        print(f"[mascot] WARNING: rendering without the mascot ({type(exc).__name__}: {exc})", flush=True)
        return None


# ---------- vertical 9:16 renderer for Shorts ----------
VW, VH = 1080, 1920
VSCALE = 1.5  # prep at 1.5x so slow zoom stays smooth


def write_ass_vertical(chunks: list[tuple[str, float, float]], path: Path) -> None:
    header = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 0\n\n"
        "[V4+ Styles]\nFormat: Name,Fontname,Fontsize,PrimaryColour,OutlineColour,BackColour,Bold,"
        "BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV\n"
        "Style: Cap,Lato,84,&H00FFFFFF,&HB0000000,&HB0000000,1,3,14,0,2,70,70,430\n\n"
        "[Events]\nFormat: Layer,Start,End,Style,Text\n"
    )
    lines = []
    for text, start, end in chunks:
        text = text.replace("\n", " ").replace("{", "(").replace("}", ")")
        lines.append(f"Dialogue: 0,{_ass_time(start)},{_ass_time(end)},Cap,{text}")
    path.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")


def _prep_vertical(src: Path, dst: Path) -> None:
    """Blurred, darkened cover of the image as background, the sharp image fitted over it (nothing cropped)."""
    from PIL import ImageEnhance, ImageFilter

    cw, ch = round(VW * VSCALE), round(VH * VSCALE)
    img = Image.open(src).convert("RGB")
    s = max(cw / img.width, ch / img.height)
    bg = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    left, top = (bg.width - cw) // 2, (bg.height - ch) // 2
    bg = bg.crop((left, top, left + cw, top + ch)).filter(ImageFilter.GaussianBlur(40))
    bg = ImageEnhance.Brightness(bg).enhance(0.45)
    f = min(cw / img.width, round(ch * 0.62) / img.height)
    fg = img.resize((round(img.width * f), round(img.height * f)), Image.LANCZOS)
    bg.paste(fg, ((cw - fg.width) // 2, round(ch * 0.40) - fg.height // 2))
    bg.save(dst, quality=92)


def make_vertical_card(title: str, path: Path) -> None:
    img = Image.new("RGB", (VW, VH), (14, 27, 61))
    d = ImageDraw.Draw(img)
    for y in range(VH):
        f = y / VH
        d.line([(0, y), (VW, y)], fill=(int(14 - 7 * f), int(27 - 13 * f), int(61 - 25 * f)))
    font = ImageFont.truetype(FONT_BOLD, 76)
    words, lines, cur = title.split(), [], ""
    for w in words:
        if len(cur) + len(w) > 16:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    lines.append(cur)
    y = 560
    for ln in lines[:5]:
        d.text((80, y), ln, font=font, fill=(255, 255, 255))
        y += 100
    img.save(path)


def _render_vclip(img: Path, frames: int, variant: int, out: Path) -> None:
    z = f"1+0.07*on/{frames}" if variant % 2 == 0 else f"1.07-0.07*on/{frames}"
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(img), "-vf",
         f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={VW}x{VH}:fps={FPS},format=yuv420p",
         "-frames:v", str(frames), "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", str(out)],
        check=True, capture_output=True,
    )


def _render_vstock(src: Path, frames: int, out: Path, offset: float = 0.0) -> None:
    graph = (f"[0:v]split[a][b];[a]scale={VW}:{VH}:force_original_aspect_ratio=increase,crop={VW}:{VH},"
             "boxblur=30:3,eq=brightness=-0.2[bg];"
             f"[b]scale={VW}:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2-160,fps={FPS},format=yuv420p[v]")
    subprocess.run(
        ["ffmpeg", "-y", "-ss", f"{offset:.2f}", "-stream_loop", "-1", "-i", str(src), "-an", "-filter_complex", graph, "-map", "[v]",
         "-frames:v", str(frames), "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", str(out)],
        check=True, capture_output=True,
    )


def render_short(script: dict, timings: list[dict], items: list[dict], narration: Path,
                 out_mp4: Path, work: Path, music: Path | None = None, look: dict = SHORT_CAPTIONS,
                 mascot: str | None = None) -> None:
    """script: {"title"}; timings: one section with timed sentences; items: [{"kind","path"}]."""
    from concurrent.futures import ThreadPoolExecutor

    from autopilot.shots import SHORT_CUT_SECONDS, SHORT_MAX_REUSE, cut_choice, plan_cuts

    work.mkdir(parents=True, exist_ok=True)
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    spans = plan_cuts([{"start": 0.0, "end": timings[-1]["end"]}], [len(items)], FPS, SHORT_CUT_SECONDS, SHORT_MAX_REUSE)[0]
    jobs = []
    for i, (a, b) in enumerate(spans):
        out = work / f"vclip_{i:03d}.mp4"
        item_idx, cycle, variant = cut_choice(i, len(items)) if items else (0, 0, i)
        item = items[item_idx] if items else None
        if item and item["kind"] == "video":
            jobs.append(("video", item["path"], b - a, 2.0 * cycle, out))
            continue
        src = item["path"] if item else work / "vcard.png"
        if not item:
            make_vertical_card(script["title"], src)
        prepped = work / f"vprep_{item_idx}.jpg"
        if not prepped.exists():
            _prep_vertical(src, prepped)
        jobs.append(("image", prepped, b - a, variant, out))

    def run(job):
        kind, src, frames, extra, out = job
        _render_vstock(src, frames, out, extra) if kind == "video" else _render_vclip(src, frames, extra, out)

    with ThreadPoolExecutor(max_workers=2) as ex:
        list(ex.map(run, jobs))
    (work / "clips.txt").write_text("".join(f"file '{j[4].name}'\n" for j in jobs))
    write_ass_words(timings, work / "captions.ass", look)
    _final_pass(work / "clips.txt", narration, work / "captions.ass", out_mp4, music,
                _mascot(narration, work, vertical=True, style=mascot) if mascot else None)
