"""Pixabay stock video search (free API, commercial use allowed, no attribution required)."""
import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://pixabay.com/api/videos/"
UA = {"User-Agent": "channel-autopilot/0.1 (https://github.com/NanduSav-1004/channel-autopilot)"}


def parse_hits(data: dict, min_width: int = 1280) -> list[dict]:
    out = []
    for h in data.get("hits", []):
        vid = h["videos"].get("medium") or h["videos"].get("large") or {}
        if not vid.get("url") or vid.get("width", 0) < min_width or h.get("duration", 0) < 4:
            continue
        if h.get("isLowQuality") or h.get("isAiGenerated"):
            continue
        out.append({
            "kind": "video", "id": h["id"], "title": h.get("tags", ""), "url": vid["url"],
            "thumb": vid["thumbnail"],
            "page": h.get("pageURL", ""), "artist": h.get("user", "unknown"),
            "license": "Pixabay Content License",
        })
    return out


def search(query: str, limit: int = 8) -> list[dict]:
    key = os.environ.get("PIXABAY_API_KEY")
    if not key:
        return []
    params = {"key": key, "q": query, "per_page": max(3, limit), "safesearch": "true"}
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers=UA)
    return parse_hits(json.load(urllib.request.urlopen(req, timeout=30)))[:limit]


def _fetch(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read())
        time.sleep(0.2)
    return path


def download_thumb(item: dict, cache: Path) -> Path:
    return _fetch(item["thumb"], cache / f"pix_{item['id']}.jpg")


def download_video(item: dict, cache: Path) -> Path:
    return _fetch(item["url"], cache / f"pix_{item['id']}.mp4")


def credit_line(item: dict) -> str:
    return f'Stock video "{item["title"][:60]}" by {item["artist"]} (Pixabay) {item["page"]}'



PHOTO_API = "https://pixabay.com/api/"


def search_photos(query: str, limit: int = 8, min_width: int = 1600) -> list[dict]:
    """Pixabay photos (same licence as the videos: commercial use, no attribution needed). AI-generated images are skipped."""
    key = os.environ.get("PIXABAY_API_KEY")
    if not key:
        return []
    params = {"key": key, "q": query, "image_type": "photo", "orientation": "horizontal", "per_page": 30, "safesearch": "true",
              "min_width": min_width}
    req = urllib.request.Request(PHOTO_API + "?" + urllib.parse.urlencode(params), headers=UA)
    hits = json.load(urllib.request.urlopen(req, timeout=30)).get("hits", [])
    return [{"kind": "photo", "id": h["id"], "url": h["largeImageURL"], "thumb": h["webformatURL"], "title": h.get("tags", ""),
             "page": h.get("pageURL", ""), "artist": h.get("user", "unknown"), "license": "Pixabay Content License"}
            for h in hits if not h.get("isAiGenerated")][:limit]


def download_photo(item: dict, cache: Path) -> Path:
    return _fetch(item["url"], cache / f"pixphoto_{item['id']}.jpg")
