"""Replace unpublished videos with newly built ones: delete the old private copy (never a public video), upload the new one private with its publish time,
and record it in the ledger. usage: python chaya/replace_upload.py <out folder> <content:id:YYYY-MM-DD HH:MM> ..."""
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
from autopilot import env, upload
from chaya import upload as chaya_upload

IST = timezone(timedelta(hours=5, minutes=30))


def sync(what: str) -> None:
    subprocess.run([str(ROOT / "scripts" / "chaya_state.sh"), what], check=True, cwd=ROOT)


out = Path(sys.argv[1])
env.load_env(ROOT / ".env")
yt = upload._client("ml")
for job in sys.argv[2:]:
    content, vid, when = job.split(":", 2)
    sync("pull")
    state = json.loads((ROOT / "data" / "chaya_state.json").read_text())
    item = state["items"].get(vid, {})
    if item.get("v3"):
        print(f"[replace] {vid} already done", flush=True)
        continue
    if not (out / vid / f"{vid}.mp4").exists():
        print(f"[replace] {vid} not built yet", flush=True)
        continue
    old = item.get("youtube_id")
    if old:
        found = yt.videos().list(part="status", id=old).execute()["items"]
        if found and found[0]["status"]["privacyStatus"] == "public":
            raise SystemExit(f"{vid}: {old} is public, not replacing it")
        if found:
            upload.delete_video(old, profile="ml")
            print(f"[replace] {vid}: deleted old private {old}", flush=True)
    new = chaya_upload.upload_private(content, out, vid, when)
    publish = datetime.strptime(when, "%Y-%m-%d %H:%M").replace(tzinfo=IST).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sync("pull")
    state = json.loads((ROOT / "data" / "chaya_state.json").read_text())
    it = state["items"].setdefault(vid, {})
    it.update({"status": "approved", "youtube_id": new, "publish_at": publish, "v3": True, "title": it.get("title") or vid, "kind": "long" if vid.endswith("_long") else "short"})
    it.pop("planned_publish_at", None)
    (ROOT / "data" / "chaya_state.json").write_text(json.dumps(state, ensure_ascii=False, indent=1))
    sync("push")
    print(f"[replace] {vid}: new {new} publishes {when} IST", flush=True)
