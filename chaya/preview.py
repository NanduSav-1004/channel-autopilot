"""Look at a storyboard before any voice exists: fake even timings, then one frame per scene and card in a contact sheet.
usage: python chaya/preview.py <content module suffix> <video id> <out png>"""
import importlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
from autopilot import motion
from chaya import build

name, vid, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
mod = importlib.import_module(f"chaya.content_{name}")
video = next(v for v in mod.VIDEOS if v["id"] == vid)
t, sents = 0.5, []
for b in video["beats"]:
    d = max(2.2, len(b["t"]) * 0.075)
    sents.append({"text": b["t"], "start": t, "end": t + d})
    t += d + 0.45
spec, _, total = build.plan(video, sents)
size = tuple(spec["canvas"])
work = out.with_suffix("")
work.mkdir(parents=True, exist_ok=True)
frames = []
with motion.Browser() as b:
    page = b.page(spec)
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.evaluate("([s, t]) => window.load(s, t)", [spec, motion._topo()])
    for i, sc in enumerate(spec["scenes"]):
        at = sc["t0"] + (sc["t1"] - sc["t0"]) * 0.8
        page.evaluate(f"window.seek({at})")
        f = work / f"{i:02d}.png"
        page.screenshot(path=str(f), clip={"x": 0, "y": 0, "width": size[0], "height": size[1]})
        frames.append(f)
if errs:
    print("PAGE ERRORS:", errs[:3])
n = len(frames)
w = 400 if size[0] > size[1] else 230
h = int(w * size[1] / size[0])
cols = 4 if size[0] > size[1] else 8
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *[a for f in frames for a in ("-i", str(f))], "-filter_complex",
                "".join(f"[{i}]scale={w}:-1[v{i}];" for i in range(n)) + "".join(f"[v{i}]" for i in range(n)) + f"xstack=inputs={n}:layout=" + "|".join(f"{(i % cols) * w}_{(i // cols) * h}" for i in range(n)), str(out)], check=True)
print("ok", n, "scenes", round(total), "s")
