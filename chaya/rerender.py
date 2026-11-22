"""Re-make the videos that are uploaded but not yet public with the current render process, upload each as a NEW private video with the same publish time,
and stop the old private video from publishing (it stays on the channel, private, to be deleted by the owner). Voices already made are reused.
usage: python chaya/rerender.py <out folder> <old output folder with narration.wav files>"""
import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
from autopilot import env, upload
from chaya import build
from chaya import upload as chaya_upload

# (video id, content module, publish time IST): soonest first
PLAN = [("electricity_long", "electricity", "2026-11-23 18:00"), ("electricity_s1", "electricity", "2026-11-24 18:00"), ("monsoon_s3", "monsoon", "2026-11-25 18:00"),
        ("electricity_s2", "electricity", "2026-11-26 18:00"), ("electricity_s3", "electricity", "2026-11-27 18:00"),
        ("petrichor_s", "batch_shorts", "2026-11-28 18:00"), ("alerts_long", "batch_alerts", "2026-11-29 18:00")]


def sync(what: str) -> None:
    subprocess.run([str(ROOT / "scripts" / "chaya_state.sh"), what], check=True, cwd=ROOT)


def main() -> None:
    out, old = Path(sys.argv[1]), Path(sys.argv[2])
    env.load_env(ROOT / ".env")
    for vid, content, when in PLAN:
        sync("pull")
        state = json.loads((ROOT / "data" / "chaya_state.json").read_text())
        item = state["items"][vid]
        if item.get("rerendered"):
            continue
        mod = importlib.import_module(f"chaya.content_{content}")
        video = next(v for v in mod.VIDEOS if v["id"] == vid)
        work = out / vid
        work.mkdir(parents=True, exist_ok=True)
        flags = set()
        if (old / vid / "narration.wav").exists() and (old / vid / "timings.json").exists():
            for f in ("narration.wav", "timings.json"):
                shutil.copy(old / vid / f, work / f)
            flags.add("--no-voice")
        print(f"[rerender] {vid} (voice reused: {bool(flags)})", flush=True)
        build.build(video, out, flags)
        new_id = chaya_upload.upload_private(content, out, vid, when)
        upload.unschedule(item["youtube_id"], profile="ml")
        sync("pull")
        state = json.loads((ROOT / "data" / "chaya_state.json").read_text())
        state["items"][vid].update({"previous_youtube_id": item["youtube_id"], "youtube_id": new_id, "rerendered": True})
        (ROOT / "data" / "chaya_state.json").write_text(json.dumps(state, ensure_ascii=False, indent=1))
        sync("push")
        print(f"[rerender] {vid}: new {new_id}, old {item['youtube_id']} unscheduled", flush=True)


if __name__ == "__main__":
    main()
