"""Build a video from an existing script + narration: python scripts/build_video.py <dir> <topic>"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, "src")
from autopilot.env import load_env
from autopilot.render import render_photo_video
from autopilot.shots import gather_images, plan_shots

load_env()
out_dir, topic = Path(sys.argv[1]), sys.argv[2]
script = json.loads(Path(sys.argv[3] if len(sys.argv) > 3 else "output/sample_script.json").read_text())
timings = json.loads((out_dir / "timings.json").read_text())
plan = plan_shots(timings)
t = time.time()
items, credits = gather_images(script, plan, Path("work/assets"), topic)
print(f"gathered in {time.time() - t:.0f}s | shots needed: {[len(p) for p in plan]}", flush=True)
print("items kept:", [len(i) for i in items], "| videos:", sum(x["kind"] == "video" for i in items for x in i), flush=True)
(out_dir / "credits.json").write_text(json.dumps(credits, indent=1))
t = time.time()
render_photo_video(script, timings, items, plan, out_dir / "narration.wav", out_dir / "final.mp4", Path("work/final"))
print(f"rendered in {time.time() - t:.0f}s", flush=True)
