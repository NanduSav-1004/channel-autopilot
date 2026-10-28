"""NASA Image and Video Library (images-api.nasa.gov): free, no key, NASA content is generally public domain. Used for space topics.
Items from non-NASA sources or flagged with copyright or permission notices are skipped."""
import hashlib
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://images-api.nasa.gov/search"
UA = {"User-Agent": "channel-autopilot/0.1 (https://github.com/NanduSav-1004/channel-autopilot)"}
NASA_CENTERS = {"JPL", "GSFC", "MSFC", "JSC", "KSC", "ARC", "GRC", "LARC", "AFRC", "SSC", "HQ", "NASA"}
BAD_NOTES = re.compile(r"copyright|©|permission|courtesy of|licensed|getty|shutterstock", re.IGNORECASE)
MAX_VIDEO_BYTES = 120 * 1024 * 1024


def _quote(url: str) -> str:
    return urllib.parse.quote(url, safe=":/?=&%~+")


def _get(url: str, limit: int | None = None) -> bytes:
    req = urllib.request.Request(_quote(url), headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read() if limit is None else r.read(limit)


def parse_results(data: dict, kind: str) -> list[dict]:
    out = []
    for it in data.get("collection", {}).get("items", []):
        meta = (it.get("data") or [{}])[0]
        links = it.get("links") or []
        center = str(meta.get("center", "")).upper()
        text = f"{meta.get('title', '')} {meta.get('description', '')} {meta.get('secondary_creator', '')}"
        if not links or center not in NASA_CENTERS or BAD_NOTES.search(text) or meta.get("media_type") != kind:
            continue
        out.append({
            "kind": kind, "source": "nasa", "id": meta["nasa_id"], "title": str(meta.get("title", ""))[:100],
            "thumb": links[0]["href"], "manifest": it.get("href", ""), "center": center,
            "page": f"https://images.nasa.gov/details/{urllib.parse.quote(meta['nasa_id'])}", "license": "NASA (public domain)",
            "artist": f"NASA/{center}" if center != "NASA" else "NASA",
        })
    return out


def search(query: str, kind: str = "image", limit: int = 12) -> list[dict]:
    params = {"q": query, "media_type": kind, "page_size": 30}
    data = json.loads(_get(API + "?" + urllib.parse.urlencode(params)))
    return parse_results(data, kind)[:limit]


def search_images(query: str) -> list[dict]:
    return search(query, "image")


def search_videos(query: str) -> list[dict]:
    return search(query, "video", 6)


def download_thumb(item: dict, cache: Path) -> Path:
    """A small picture of the item (an image's thumbnail, a video's preview frame) for the relevance rating."""
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / ("nasa_" + hashlib.sha1(item["thumb"].encode()).hexdigest()[:16] + ".jpg")
    if not path.exists():
        path.write_bytes(_get(item["thumb"]))
    return path


def _variants(item: dict) -> list[str]:
    try:
        return [u for u in json.loads(_get(item["manifest"])) if isinstance(u, str)]
    except (OSError, ValueError):
        return []


def download_image(item: dict, cache: Path) -> Path:
    """The best size that exists: large, then medium, then the original (the manifest lists what is actually there)."""
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / ("nasa_full_" + hashlib.sha1(item["thumb"].encode()).hexdigest()[:16] + ".jpg")
    if path.exists():
        return path
    files = _variants(item)
    for tag in ("~large.jpg", "~medium.jpg", "~orig.jpg"):
        for u in files:
            if u.lower().endswith(tag):
                try:
                    path.write_bytes(_get(u))
                    return path
                except OSError:
                    continue
    return download_thumb(item, cache)


def download_video(item: dict, cache: Path) -> Path:
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / ("nasa_" + hashlib.sha1(item["thumb"].encode()).hexdigest()[:16] + ".mp4")
    if path.exists():
        return path
    files = _variants(item)
    for tag in ("~medium.mp4", "~large.mp4", "~mobile.mp4"):
        for u in files:
            if u.lower().endswith(tag):
                req = urllib.request.Request(_quote(u), headers={**UA, "Range": "bytes=0-0"})
                try:
                    with urllib.request.urlopen(req, timeout=60) as r:
                        total = int(str(r.headers.get("Content-Range", "/0")).rsplit("/", 1)[-1] or 0)
                except (OSError, ValueError):
                    total = 0
                if total and total > MAX_VIDEO_BYTES:
                    continue
                try:
                    path.write_bytes(_get(u))
                    return path
                except OSError:
                    continue
    raise OSError(f"no usable video file for {item['id']}")


def credit_line(item: dict) -> str:
    return f'{item["kind"].capitalize()} "{item["title"][:70]}": {item["artist"]} (NASA Image and Video Library) {item["page"]}'
