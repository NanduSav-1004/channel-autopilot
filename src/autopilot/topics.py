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


def discover(
    conn: sqlite3.Connection, niche: str, n: int, gen: Callable = llm.generate_json,
    fetch: Callable = wiki.fetch_source, forbidden: list[str] | None = None, min_source_chars: int = 2500,
) -> list[int]:
    """Queue up to n verified, non-duplicate long-form jobs. Returns the new job ids."""
    known = db.known_topics(conn)
    out = gen(PROMPT.format(n=n * 2, niche=niche, known=", ".join(sorted(known)[:80]) or "none"))
    added: list[int] = []
    for cand in out.get("topics", []):
        topic, title = cand.get("topic", "").strip(), cand.get("wikipedia_title", "").strip()
        if not topic or not title or len(added) >= n:
            continue
        if any(f.lower() in f"{topic} {title}".lower() for f in forbidden or []):
            continue
        if topic.lower() in known or title.lower() in known:
            continue
        src = fetch(title)
        if not src or not _same_article(title, src["title"]) or len(src["text"]) < min_source_chars:
            continue  # no real article, or too thin to ground a full script
        known |= {topic.lower(), src["title"].lower()}
        added.append(db.add_job(conn, topic, "long", src["title"]))
    return added
