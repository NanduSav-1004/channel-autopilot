"""Set the channel description (and keywords) from assets/brand/channel_description.txt.

Line breaks are sent as CRLF: with bare LF, YouTube's About page shows a stray "|" at each paragraph break.
Every other branding setting (name, banner, ...) is read first and written back unchanged.

usage: python scripts/set_channel_description.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, "src")
from googleapiclient.discovery import build

from autopilot.env import load_env
from autopilot.youtube_auth import load_credentials

KEYWORDS = '"science explainers" physics chemistry engineering "how things work" "history of science" "technology explained" educational'

load_env()
yt = build("youtube", "v3", credentials=load_credentials())
desc = Path("assets/brand/channel_description.txt").read_text().strip().replace("\r\n", "\n").replace("\n", "\r\n")
assert len(desc) <= 1000 and len(KEYWORDS) <= 500
ch = yt.channels().list(part="brandingSettings", mine=True).execute()["items"][0]
new = json.loads(json.dumps(ch["brandingSettings"]))
new["channel"]["description"], new["channel"]["keywords"] = desc, KEYWORDS
yt.channels().update(part="brandingSettings", body={"id": ch["id"], "brandingSettings": new}).execute()
print("channel description updated")
