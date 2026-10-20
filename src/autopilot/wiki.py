"""Wikipedia source fetch: grounds scripts in real text so facts can be checked."""
import json
import urllib.parse
import urllib.request

API = "https://en.wikipedia.org/w/api.php"
UA = {"User-Agent": "channel-autopilot/0.1 (https://github.com/NanduSav-1004/channel-autopilot)"}


def _get(params: dict) -> dict:
    url = API + "?" + urllib.parse.urlencode({**params, "format": "json", "formatversion": 2})
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))


def fetch_source(topic: str, max_chars: int = 9000) -> dict | None:
    """Return {title, url, text} for the best-matching article, or None."""
    hits = _get({"action": "query", "list": "search", "srsearch": topic, "srlimit": 1})
    results = hits["query"]["search"]
    if not results:
        return None
    title = results[0]["title"]
    page = _get({"action": "query", "prop": "extracts", "explaintext": 1, "titles": title})
    text = page["query"]["pages"][0].get("extract", "")
    url = "https://en.wikipedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))
    return {"title": title, "url": url, "text": text[:max_chars]}
