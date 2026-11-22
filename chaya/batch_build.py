"""Build several videos locally, reusing saved voices where they exist.
usage: python chaya/batch_build.py <out folder> <content:id:voice_dir_or_-> ..."""
import importlib
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
from autopilot import env
from chaya import build

out = Path(sys.argv[1])
env.load_env(ROOT / ".env")
for job in sys.argv[2:]:
    content, vid, voice = job.split(":", 2)
    video = next(v for v in importlib.import_module(f"chaya.content_{content}").VIDEOS if v["id"] == vid)
    work = out / vid
    work.mkdir(parents=True, exist_ok=True)
    flags = set()
    if voice != "-" and (Path(voice) / vid / "narration.wav").exists():
        for f in ("narration.wav", "timings.json"):
            shutil.copy(Path(voice) / vid / f, work / f)
        flags.add("--no-voice")
    if (work / f"{vid}.mp4").exists():
        print(f"[batch] {vid} already built", flush=True)
        continue
    print(f"[batch] {vid} (voice reused: {bool(flags)})", flush=True)
    build.build(video, out, flags)
    print(f"[batch] {vid} done", flush=True)
