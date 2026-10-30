"""Motion graphics for the data channel: scenes are drawn in a headless Chrome (assets/motion/stage.html), one screenshot per
frame, and piped into ffmpeg. Every frame is a pure function of time, so a scene can be split into chunks that render in
parallel (one Chrome each) and are joined afterwards."""
import json
import multiprocessing
import os
import shutil
import subprocess
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

STAGE = Path(__file__).resolve().parents[2] / "assets" / "motion"
FPS = 30
GRAIN = "noise=alls=5:allf=u"   # a fixed film grain, added by ffmpeg (cheaper than drawing it in the page)


def _chrome() -> str | None:
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        if path := shutil.which(name):
            return path
    return None


def _topo() -> dict:
    return {"states": json.loads((STAGE / "vendor" / "states-albers-10m.json").read_text())}


CHROME_MB = 900        # rough memory one rendering Chrome needs at 1080p


def workers() -> int:
    """Parallel Chromes: one per spare CPU core, but never more than the free memory can hold."""
    try:
        info = Path("/proc/meminfo").read_text().splitlines()
        avail = int(next(ln for ln in info if ln.startswith("MemAvailable")).split()[1]) // 1024
    except (OSError, StopIteration, ValueError):
        avail = 4096
    return max(1, min(6, (os.cpu_count() or 2) - 1, (avail - 1024) // CHROME_MB))


def _encode(out: Path, w: int, h: int, fps: int) -> subprocess.Popen:
    return subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-",
                             "-vf", GRAIN, "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-s", f"{w}x{h}",
                             "-r", str(fps), str(out)], stdin=subprocess.PIPE)


def _render_frames(page, spec: dict, first: int, last: int, out: Path, fps: int) -> None:
    w, h = spec.get("width", 1920), spec.get("height", 1080)
    page.evaluate("([s, t]) => window.load(s, t)", [spec, _topo() if spec["type"] == "map" else None])
    ff = _encode(out, w, h, fps)
    try:
        for i in range(first, last):
            page.evaluate(f"window.seek({i / fps})")
            ff.stdin.write(page.screenshot(type="jpeg", quality=94, clip={"x": 0, "y": 0, "width": w, "height": h}))
    finally:
        ff.stdin.close()
        ff.wait()
    if ff.returncode:
        raise RuntimeError(f"ffmpeg failed for scene {spec['type']}")


def _chunk(args) -> str:
    spec, first, last, out, fps = args
    with Browser() as b:
        _render_frames(b.page(spec), spec, first, last, Path(out), fps)
    return out


def render_scene(spec: dict, out: Path, fps: int = FPS, jobs: int | None = None) -> Path:
    """Render one scene spec ({"type", "duration", ...}) to an H.264 file at `out`."""
    frames = round(spec["duration"] * fps)
    jobs = max(1, min(jobs or workers(), frames // fps or 1))
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        cuts = [round(frames * k / jobs) for k in range(jobs + 1)]
        parts = [(spec, cuts[k], cuts[k + 1], str(Path(tmp) / f"part{k}.mp4"), fps) for k in range(jobs)]
        if jobs == 1:
            _chunk(parts[0])
        else:
            with ProcessPoolExecutor(jobs, mp_context=multiprocessing.get_context("fork")) as ex:  # works without a __main__ guard
                list(ex.map(_chunk, parts))
        (Path(tmp) / "list.txt").write_text("".join(f"file '{p[3]}'\n" for p in parts))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(Path(tmp) / "list.txt"),
                        "-c", "copy", str(out)], check=True)
    return out


_worker_browser = None


def _init_worker() -> None:
    """Each worker process keeps one Chrome for all its chunks; it is closed when the pool shuts down."""
    from multiprocessing import util

    global _worker_browser
    _worker_browser = Browser().__enter__()
    util.Finalize(None, _worker_browser.__exit__, args=(None, None, None), exitpriority=10)


def _work(args) -> str:
    spec, first, last, out, fps = args
    _render_frames(_worker_browser.page(spec), spec, first, last, Path(out), fps)
    return out


def render_many(specs: list[dict], out_dir: Path, fps: int = FPS, jobs: int | None = None, chunk_seconds: float = 4.0) -> list[Path]:
    """Render many scenes with a pool of long-lived Chromes: every scene is cut into chunks of a few seconds, all chunks are
    shared out across the workers, and each scene's chunks are joined in order. Returns one file per scene."""
    out_dir.mkdir(parents=True, exist_ok=True)
    tasks, per_scene = [], []
    for i, spec in enumerate(specs):
        frames = max(1, round(spec["duration"] * fps))
        step = max(1, round(chunk_seconds * fps))
        parts = []
        for k, first in enumerate(range(0, frames, step)):
            path = out_dir / f"s{i:03d}_{k:03d}.mp4"
            parts.append(path)
            tasks.append((spec, first, min(frames, first + step), str(path), fps))
        per_scene.append(parts)
    tasks.sort(key=lambda a: -(a[2] - a[1]))       # longest chunks first keeps every worker busy to the end
    with ProcessPoolExecutor(jobs or workers(), mp_context=multiprocessing.get_context("fork"), initializer=_init_worker) as ex:
        list(ex.map(_work, tasks))
    outs = []
    for i, parts in enumerate(per_scene):
        listing = out_dir / f"s{i:03d}.txt"
        listing.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
        out = out_dir / f"scene{i:03d}.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(out)], check=True)
        for p in parts:
            p.unlink()
        outs.append(out)
    return outs


class Browser:
    """One headless Chrome, with a page per frame size."""

    def __enter__(self):
        from playwright.sync_api import sync_playwright

        self._pw = sync_playwright().start()
        exe = _chrome()
        args = ["--force-color-profile=srgb", "--hide-scrollbars"]
        self._b = self._pw.chromium.launch(executable_path=exe, args=args) if exe else self._pw.chromium.launch(args=args)
        self._pages: dict = {}
        return self

    def page(self, spec: dict):
        size = (spec.get("width", 1920), spec.get("height", 1080))
        if size not in self._pages:
            p = self._b.new_page(viewport={"width": size[0], "height": size[1]}, device_scale_factor=1)
            p.goto((STAGE / "stage.html").as_uri())
            p.wait_for_function("typeof window.load === 'function'")
            self._pages[size] = p
        return self._pages[size]

    def __exit__(self, *exc):
        self._b.close()
        self._pw.stop()
