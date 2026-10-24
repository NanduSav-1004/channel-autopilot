"""Set a channel's banner, description, keywords, country and default language through the API.

usage: python scripts/set_channel_branding.py ml        (the Malayalam channel; needs secrets/token_ml.json)
Every other branding setting (title, trailer, ...) is read first and written back unchanged. The profile picture and the
handle cannot be set through the API: do those in YouTube Studio (Customization).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, "src")
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from autopilot.env import load_env
from autopilot.youtube_auth import load_credentials

PROFILES = {
    "ml": {"dir": Path("assets/brand_ml"), "country": "IN", "language": "ml",
           "keywords": '"ശാസ്ത്രം" "മലയാളം" "science malayalam" "malayalam science" physics chemistry technology explained "how things work"'},
}


def main(profile: str) -> None:
    cfg = PROFILES[profile]
    load_env()
    yt = build("youtube", "v3", credentials=load_credentials(profile))
    desc = (cfg["dir"] / "channel_description.txt").read_text().strip().replace("\r\n", "\n").replace("\n", "\r\n")
    assert len(desc) <= 1000 and len(cfg["keywords"]) <= 500, "description or keywords too long"
    ch = yt.channels().list(part="brandingSettings,snippet", mine=True).execute()["items"][0]
    print("channel:", ch["snippet"]["title"], ch["id"])
    banner = yt.channelBanners().insert(
        media_body=MediaFileUpload(str(cfg["dir"] / "banner.jpg"), mimetype="image/jpeg")).execute()
    new = json.loads(json.dumps(ch["brandingSettings"]))
    new.setdefault("channel", {}).update({"description": desc, "keywords": cfg["keywords"],
                                          "country": cfg["country"], "defaultLanguage": cfg["language"]})
    new.setdefault("image", {})["bannerExternalUrl"] = banner["url"]
    yt.channels().update(part="brandingSettings", body={"id": ch["id"], "brandingSettings": new}).execute()
    print("banner, description, keywords, country and default language set")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "ml")
