"""Search demand from YouTube's autocomplete (free, public). A question that appears after only a few typed
words is one many people search for: those make the best topics for a channel with no audience yet."""
import json
import time
import urllib.parse
import urllib.request
from collections.abc import Callable

URL = "https://suggestqueries.google.com/complete/search"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) channel-autopilot/0.1"}
REGION = "us"  # the audience is US/UK, and results otherwise follow the server's location


def suggest(query: str) -> list[str]:
    """Autocomplete suggestions for what a US viewer has typed so far. [] on any failure (fail soft)."""
    params = {"client": "firefox", "ds": "yt", "q": query, "gl": REGION, "hl": "en"}
    try:
        req = urllib.request.Request(URL + "?" + urllib.parse.urlencode(params), headers=UA)
        data = json.loads(urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "replace"))
        time.sleep(0.15)  # be polite
        return [str(s) for s in data[1]]
    except (OSError, ValueError, IndexError, KeyError):
        return []


def _norm(text: str) -> str:
    return " ".join("".join(c.lower() if c.isalnum() else " " for c in text).split())


LONG_QUERY_WORDS = 5   # nobody types more than this; score the opening words instead, at a discount
LONG_QUERY_DISCOUNT = 0.7


def demand_score(query: str, suggest_fn: Callable[[str], list[str]] = suggest) -> float:
    """0..1. Type the question a few words at a time; the sooner (and higher) it shows up in the suggestions,
    the more people search for it. 0 means it never appeared (or autocomplete is unreachable)."""
    words = _norm(query).split()
    if len(words) > LONG_QUERY_WORDS:
        full = _exact_score(" ".join(words), suggest_fn)
        head = _exact_score(" ".join(words[:LONG_QUERY_WORDS - 1]), suggest_fn) * LONG_QUERY_DISCOUNT
        return round(max(full, head), 3)
    return _exact_score(" ".join(words), suggest_fn)


def _exact_score(query: str, suggest_fn: Callable[[str], list[str]]) -> float:
    words = query.split()
    if len(words) < 2:
        return 0.0
    target = " ".join(words)
    for typed in range(2, len(words) + 1):
        sugg = [_norm(s) for s in suggest_fn(" ".join(words[:typed]))]
        for rank, s in enumerate(sugg):
            if s == target or s.startswith(target):  # the suggestion IS this question (maybe with a tail)
                earliness = 1 - (typed - 2) / max(1, len(words) - 1)  # found after fewer words = more popular
                return round(earliness * (1 - rank / 12), 3)
    return 0.0
