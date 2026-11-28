"""Look at one hand-made scene at several moments: python chaya/scene_preview.py <kind> <p json file> <out png> [wide|tall] [seconds=14]"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
from autopilot import motion

kind, pf, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
orient = sys.argv[4] if len(sys.argv) > 4 else "wide"
dur = float(sys.argv[5]) if len(sys.argv) > 5 else 14.0
size = (1920, 1080) if orient == "wide" else (1080, 1920)
spec = {"type": "chaya", "duration": dur, "scenes": [{"kind": kind, "t0": 0, "t1": dur, "tr": "cut", "p": json.loads(pf.read_text())}], "cards": [], "beats": [0.2], "canvas": list(size), "width": size[0], "height": size[1], "grain": False}
work = out.with_suffix("")
work.mkdir(parents=True, exist_ok=True)
frames = []
with motion.Browser() as b:
    page = b.page(spec)
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.evaluate("([s, t]) => window.load(s, t)", [spec, motion._topo()])
    for i in range(8):
        page.evaluate(f"window.seek({dur * (i + 0.5) / 8})")
        f = work / f"{i:02d}.png"
        page.screenshot(path=str(f), clip={"x": 0, "y": 0, "width": size[0], "height": size[1]})
        frames.append(f)
if errs:
    print("PAGE ERRORS:", errs[:3])
w = 480 if orient == "wide" else 270
h = int(w * size[1] / size[0])
cols = 4
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *[a for f in frames for a in ("-i", str(f))], "-filter_complex",
                "".join(f"[{i}]scale={w}:-1[v{i}];" for i in range(8)) + "".join(f"[v{i}]" for i in range(8)) + "xstack=inputs=8:layout=" + "|".join(f"{(i % cols) * w}_{(i // cols) * h}" for i in range(8)), str(out)], check=True)
print("ok")
