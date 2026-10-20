"""Wikimedia Commons image search. Only commercially reusable licenses; records attribution."""
import hashlib
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "channel-autopilot/0.1 (https://github.com/NanduSav-1004/channel-autopilot)"}
# Reject NC/ND/unknown. Allow CC0, public domain, CC BY, CC BY-SA.
LICENSE_OK = re.compile(r"^(CC0|Public domain|PD|CC BY(-SA)? [\d.]+)", re.IGNORECASE)
LICENSE_BAD = re.compile(r"\b(NC|ND)\b", re.IGNORECASE)


def _strip_tags(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html or "")).strip()


def license_ok(name: str) -> bool:
    return bool(LICENSE_OK.match(name or "")) and not LICENSE_BAD.search(name or "")


def parse_results(data: dict, min_width: int = 1000) -> list[dict]:
    out = []
    for page in data.get("query", {}).get("pages", []):
        info = (page.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata", {})
        lic = meta.get("LicenseShortName", {}).get("value", "")
        w, h = info.get("width", 0), info.get("height", 0)
        if info.get("mime") not in ("image/jpeg", "image/png") or not license_ok(lic):
            continue
        if w < min_width or h == 0 or w / h < 1.2:  # landscape only, avoids ugly crops
            continue
        out.append({
            "kind": "image", "title": page["title"], "thumb": info.get("thumburl") or info["url"],
            "page": info.get("descriptionurl", ""), "license": lic,
            "artist": _strip_tags(meta.get("Artist", {}).get("value", "")) or "unknown",
        })
    return out


def search(query: str, limit: int = 20) -> list[dict]:
    params = {
        "action": "query", "generator": "search", "gsrsearch": f"{query} filetype:bitmap",
        "gsrnamespace": 6, "gsrlimit": limit, "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata", "iiurlwidth": 1920,
        "format": "json", "formatversion": 2,
    }
    url = API + "?" + urllib.parse.urlencode(params)
    data = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))
    return parse_results(data)


def download(item: dict, cache: Path) -> Path:
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / (hashlib.sha1(item["thumb"].encode()).hexdigest()[:16] + ".jpg")
    if not path.exists():
        req = urllib.request.Request(item["thumb"], headers=UA)
        path.write_bytes(urllib.request.urlopen(req, timeout=60).read())
        time.sleep(0.3)  # be polite to Commons
    return path


def credit_line(item: dict) -> str:
    return f'"{item["title"].removeprefix("File:")}" by {item["artist"]} ({item["license"]}) {item["page"]}'
