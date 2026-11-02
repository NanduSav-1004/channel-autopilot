"""Cross-transitions between the cuts of a photo video, using ffmpeg's built-in `xfade` (no new tool).

The video must stay exactly as long as before (the voice and the captions are timed to it). So a clip that is followed by a transition is
rendered `N` frames LONGER; its last `N` frames are blended with the first `N` frames of the next clip, and the next clip carries on from
its frame `N`. Total frame count is unchanged. Data-shot clips are never touched. Any problem (an ffmpeg error, a wrong frame count) puts
every clip back to its planned length and plain cuts are used: a transition is an extra."""
import subprocess
from collections.abc import Callable
from pathlib import Path

FPS = 24
N = 10                                  # frames per transition (about 0.4 s)
EVERY = 2                               # a transition on every second cut, so the pace still varies
STYLES = ["fade", "slideleft", "dissolve", "wipeleft", "smoothleft", "circleopen", "fadeblack", "slideright"]
MIN_FRAMES = 2 * N + 6                  # both neighbours must be at least this long


def parse_count(text: str) -> int:
    """ffprobe prints the count as '58' for most files but '58,' (a trailing comma, from an empty extra field) for some: take the first integer."""
    import re

    m = re.search(r"\d+", text)
    if not m:
        raise ValueError(f"no frame count in {text!r}")
    return int(m.group())


def frame_count(path: Path) -> int:
    out = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames",
                          "-of", "csv=p=0", str(path)], check=True, capture_output=True, text=True).stdout.strip()
    return parse_count(out)


def plan(kinds: list[str], frames: list[int], every: int = EVERY) -> list[str | None]:
    """The transition INTO each clip (None for none): only between two non-data-shot clips that are both long enough, one cut in `every`."""
    out: list[str | None] = [None] * len(kinds)
    k = 0
    for i in range(1, len(kinds)):
        if "datashot" in (kinds[i], kinds[i - 1]) or min(frames[i], frames[i - 1]) < MIN_FRAMES:
            continue
        if k % every == 0:
            out[i] = STYLES[(k // every) % len(STYLES)]
        k += 1
    return out


def _trim(src: Path, a: int, b: int, out: Path, fps: int) -> None:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vf", f"trim=start_frame={a}:end_frame={b},setpts=PTS-STARTPTS",
                    "-r", str(fps), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", str(out)], check=True)


def _blend(a: Path, a0: int, a1: int, b: Path, b0: int, b1: int, style: str, out: Path, fps: int) -> None:
    g = (f"[0:v]trim=start_frame={a0}:end_frame={a1},setpts=PTS-STARTPTS[x];[1:v]trim=start_frame={b0}:end_frame={b1},setpts=PTS-STARTPTS[y];"
         f"[x][y]xfade=transition={style}:duration={(N - 0.5) / fps:.4f}:offset=0,fps={fps},format=yuv420p[v]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(a), "-i", str(b), "-filter_complex", g, "-map", "[v]", "-frames:v", str(N),
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", str(out)], check=True)


def lengths(frames: list[int], styles: list[str | None]) -> list[int]:
    """How many frames each clip must be rendered with: N more when the next clip is entered through a transition."""
    return [f + (N if i + 1 < len(styles) and styles[i + 1] else 0) for i, f in enumerate(frames)]


def apply(files: list[Path], frames: list[int], styles: list[str | None], work: Path, fps: int = FPS,
          log: Callable[[str], None] = print) -> list[Path]:
    """The clips to concatenate. `files[i]` was rendered with lengths(frames, styles)[i] frames. Same total as sum(frames), or plain cuts."""
    want = lengths(frames, styles)
    tdir = work / "xfade"
    tdir.mkdir(parents=True, exist_ok=True)

    def plain() -> list[Path]:                                   # every clip back to its planned length
        out = []
        for i, f in enumerate(files):
            if want[i] == frames[i]:
                out.append(f)
            else:
                _trim(f, 0, frames[i], tdir / f"p{i:04d}.mp4", fps)
                out.append(tdir / f"p{i:04d}.mp4")
        return out

    if not any(styles):
        return files
    try:
        if [frame_count(f) for f in files] != want:
            raise ValueError("a clip does not have the planned number of frames")
        out: list[Path] = []
        n_trans = 0
        for i, f in enumerate(files):
            head = N if styles[i] else 0                         # frames of this clip already shown inside the transition
            if styles[i]:
                _blend(files[i - 1], frames[i - 1], frames[i - 1] + N, f, 0, N, styles[i], tdir / f"t{i:04d}.mp4", fps)
                out.append(tdir / f"t{i:04d}.mp4")
                n_trans += 1
            if head or want[i] != frames[i]:
                p = tdir / f"c{i:04d}.mp4"
                _trim(f, head, frames[i] if want[i] != frames[i] else want[i], p, fps)
                out.append(p)
            else:
                out.append(f)
        total = sum(frame_count(p) for p in out)
        if total != sum(frames):
            raise ValueError(f"frame count changed ({sum(frames)} -> {total})")
        log(f"[transitions] {n_trans} cross-transitions, length unchanged ({total} frames)")
        return out
    except Exception as exc:  # noqa: BLE001
        log(f"[transitions] skipped ({type(exc).__name__}: {exc})")
        return plain()
