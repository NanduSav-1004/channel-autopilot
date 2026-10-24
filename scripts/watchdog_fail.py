"""Telegram alert for a failed workflow run (the daily command alerts itself when it ends with no video; this covers
crashes before that, such as a failed install or a timeout)."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from autopilot import notify

run = f"https://github.com/{os.environ.get('GITHUB_REPOSITORY', '')}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"
from datetime import datetime, timedelta, timezone

n = datetime.now(timezone.utc)
notify.send(f"Brightwork: the daily workflow FAILED at {(n + timedelta(hours=5, minutes=30)).strftime('%I:%M %p').lstrip('0')} IST / {n:%H:%M} UTC. {run}")
