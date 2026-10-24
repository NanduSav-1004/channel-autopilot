"""Alerts (Telegram) if today's long video has not been uploaded by the time this runs. Reads the `state` branch.

usage: python scripts/watchdog.py   (env: GITHUB_REPOSITORY, GITHUB_TOKEN, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
"""
import os
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from autopilot import notify


def uploaded_today(db_path: str) -> int:
    conn = sqlite3.connect(db_path)
    return conn.execute("SELECT COUNT(*) FROM jobs WHERE kind = 'long' AND video_id IS NOT NULL "
                        "AND date(created_at) = date('now')").fetchone()[0]


def now_ist() -> str:
    from datetime import datetime, timedelta, timezone

    n = datetime.now(timezone.utc)
    return f"{(n + timedelta(hours=5, minutes=30)).strftime('%I:%M %p').lstrip('0')} IST / {n:%H:%M} UTC"


def main() -> None:
    remote = f"https://x-access-token:{os.environ['GITHUB_TOKEN']}@github.com/{os.environ['GITHUB_REPOSITORY']}.git"
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["git", "init", "-q", tmp], check=True)
        subprocess.run(["git", "-C", tmp, "fetch", "-q", "--depth=1", remote, "state"], check=True)
        db = Path(tmp) / "autopilot.db"
        db.write_bytes(subprocess.run(["git", "-C", tmp, "show", "FETCH_HEAD:data/autopilot.db"], check=True, capture_output=True).stdout)
        n = uploaded_today(str(db))
    if n:
        print(f"ok: {n} long video(s) uploaded today")
        return
    msg = ("Brightwork WATCHDOG: no video has been uploaded yet today (checked at "
           f"{now_ist()}). Start the run by hand: "
           "https://github.com/NanduSav-1004/channel-autopilot/actions/workflows/daily.yml (Run workflow, tick live, privacy public)")
    print(msg)
    notify.send(msg)
    sys.exit(1)


if __name__ == "__main__":
    main()
