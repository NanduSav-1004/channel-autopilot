"""Put the new logo badge on the thumbnails of existing long videos (both channels).

usage: python scripts/refresh_badges.py [--apply]     (without --apply it only reports what it would change)
It reads each long video's current thumbnail from YouTube, and where the OLD round "B" badge is found in the top-right it paints the
new logo over it (the new badge is larger, so it fully covers the old one), then uploads the result. Thumbnails without the old
badge (automatic frames, or already updated) are left alone.
"""
import io
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, "src")
import numpy as np
from PIL import Image

from autopilot import thumbnail, upload
from autopilot.env import load_env

W = 1280


def has_old_badge(img: Image.Image) -> bool:
    """The old badge: a navy disc (radius 56) with an amber ring at about (W-96, 92)."""
    a = np.asarray(img.convert("RGB").resize((1280, 720))).astype(int)
    cx, cy = W - 96, 92
    disc = a[cy - 20: cy + 20, cx - 20: cx + 20].reshape(-1, 3).mean(axis=0)       # navy centre (with the white B on it)
    ys, xs = np.mgrid[-70:71, -70:71]
    ring = np.hypot(xs, ys)
    band = (ring >= 50) & (ring <= 58)
    px = a[cy - 70: cy + 71, cx - 70: cx + 71][band]
    amber = ((px[:, 0] > 200) & (px[:, 1] > 130) & (px[:, 2] < 110)).mean()        # most of the ring is amber
    return bool(amber > 0.45 and disc[2] > disc[0] and disc.max() < 235)


def long_videos(profile: str) -> list[dict]:
    yt = upload._client(profile)
    pl = yt.channels().list(part="contentDetails", mine=True).execute()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, tok = [], None
    while True:
        r = yt.playlistItems().list(part="contentDetails", playlistId=pl, maxResults=50, pageToken=tok).execute()
        ids += [i["contentDetails"]["videoId"] for i in r["items"]]
        tok = r.get("nextPageToken")
        if not tok:
            break
    out = []
    for i in range(0, len(ids), 50):
        for v in yt.videos().list(part="snippet,contentDetails,status", id=",".join(ids[i:i + 50])).execute()["items"]:
            d = v["contentDetails"]["duration"]                                    # PT11M40S
            h, m, s = (int(x or 0) for x in re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d).groups())
            if h * 3600 + m * 60 + s >= 180:
                out.append({"id": v["id"], "title": v["snippet"]["title"], "thumbs": v["snippet"]["thumbnails"],
                            "privacy": v["status"]["privacyStatus"]})
    return out


def main(apply: bool) -> None:
    load_env()
    work = Path("work/badges")
    work.mkdir(parents=True, exist_ok=True)
    for profile in ("en", "ml"):
        print(f"== {profile}")
        for v in long_videos(profile):
            thumbs = v["thumbs"]
            url = (thumbs.get("maxres") or thumbs.get("high"))["url"]
            try:
                img = Image.open(io.BytesIO(urllib.request.urlopen(url, timeout=30).read())).convert("RGB")
            except OSError as exc:
                print(f"   {v['id']} {v['privacy']:8} skipped (thumbnail not readable yet: {exc})")
                continue
            if img.size != (1280, 720):
                img = img.resize((1280, 720), Image.LANCZOS)
            if not has_old_badge(img):
                print(f"   {v['id']} {v['privacy']:8} left alone (no old badge)  {v['title'][:50]}")
                continue
            canvas = img.convert("RGBA")
            thumbnail._draw_badge(canvas, "ml" if profile == "ml" else "en")
            out = work / f"{profile}_{v['id']}.jpg"
            canvas.convert("RGB").save(out, quality=92)
            if apply:
                upload.set_thumbnail(v["id"], out, profile=profile)
            print(f"   {v['id']} {v['privacy']:8} {'UPDATED' if apply else 'would update'}  {v['title'][:50]}")


if __name__ == "__main__":
    main("--apply" in sys.argv)
