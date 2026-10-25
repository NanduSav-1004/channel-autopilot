"""Telegram alert for a failed workflow run (the daily command alerts itself when it ends with no video; this covers
crashes before that, such as a failed install or a timeout)."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import re

from autopilot import notify

KEYS = re.compile(r"(AIza[0-9A-Za-z_-]{20,}|gsk_[0-9A-Za-z]{16,}|GOCSPX-[0-9A-Za-z_-]{8,}|ya29\.[0-9A-Za-z_-]{20,}|1//[0-9A-Za-z_-]{20,}|\d{8,}:[0-9A-Za-z_-]{30,})")
tail = ""
if Path("run.log").exists():          # the last lines say WHY it failed, so the alert is enough to decide what to do
    lines = [ln for ln in Path("run.log").read_text(errors="replace").splitlines() if ln.strip()][-6:]
    tail = "\n\nLast log lines:\n" + KEYS.sub("***", "\n".join(ln[:240] for ln in lines))
run = f"https://github.com/{os.environ.get('GITHUB_REPOSITORY', '')}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"
from datetime import datetime, timedelta, timezone

n = datetime.now(timezone.utc)
notify.send(f"Brightwork: the daily workflow FAILED at {(n + timedelta(hours=5, minutes=30)).strftime('%I:%M %p').lstrip('0')} IST / {n:%H:%M} UTC. {run}{tail}")
