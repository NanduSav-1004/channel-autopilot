"""Topic discovery: LLM brainstorm of evergreen topics, each verified against a real Wikipedia article."""
import sqlite3
from collections.abc import Callable

from autopilot import db, llm, wiki

PROMPT = """Suggest {n} topics for a YouTube channel about: {niche}.
Each must be an evergreen concept, device, discovery or phenomenon that has its own Wikipedia article
(physics, chemistry, engineering, space, computing, inventions, history of science).
Do NOT suggest: medicine or health, diseases, diet, finance, law, politics, current events, or living people.
Prefer topics with a surprising "why" or "how" that make people curious. Vary the areas.
Already covered, do not repeat: {known}

Return JSON: {{"topics": [{{"topic": str, "wikipedia_title": str}}]}}"""


def _same_article(wanted: str, found: str) -> bool:
    a, b = wanted.lower().strip(), found.lower().strip()
    return a == b or a in b or b in a


def _candidates(out) -> list[dict]:
    """The model is asked for {"topics": [...]}, but tolerate a renamed key or a bare list."""
    if isinstance(out, list):
        lst = out
    elif isinstance(out, dict):
        lst = out.get("topics") or next((v for v in out.values() if isinstance(v, list)), [])
    else:
        lst = []
    return [c for c in lst if isinstance(c, dict)]


def discover(
    conn: sqlite3.Connection, niche: str, n: int, gen: Callable = llm.generate_json,
    fetch: Callable = wiki.fetch_source, forbidden: list[str] | None = None, min_source_chars: int = 2500,
) -> list[int]:
    """Queue up to n verified, non-duplicate long-form jobs. Returns the new job ids."""
    known = db.known_topics(conn)
    out = gen(PROMPT.format(n=n * 2, niche=niche, known=", ".join(sorted(known)[:80]) or "none"))
    candidates = _candidates(out)
    print(f"[topics] LLM proposed {len(candidates)} candidate(s); need {n}", flush=True)
    added: list[int] = []
    for cand in candidates:
        topic, title = str(cand.get("topic", "")).strip(), str(cand.get("wikipedia_title", "")).strip()
        if len(added) >= n:
            break
        reason = None
        if not topic or not title:
            reason = "missing topic or title"
        elif any(f.lower() in f"{topic} {title}".lower() for f in forbidden or []):
            reason = "forbidden theme"
        elif topic.lower() in known or title.lower() in known:
            reason = "already covered"
        else:
            src = fetch(title)
            if not src:
                reason = "no Wikipedia article found"
            elif not _same_article(title, src["title"]):
                reason = f"search returned a different article ({src['title']!r})"
            elif len(src["text"]) < min_source_chars:
                reason = f"article too thin ({len(src['text'])} < {min_source_chars} chars)"
        if reason:
            print(f"[topics] rejected {title or topic!r}: {reason}", flush=True)
            continue
        known |= {topic.lower(), src["title"].lower()}
        added.append(db.add_job(conn, topic, "long", src["title"]))
        print(f"[topics] queued {topic!r} (source: {src['title']!r}, {len(src['text'])} chars)", flush=True)
    return added
