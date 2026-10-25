"""Topic discovery: the LLM brainstorms evergreen questions, real search demand ranks them, and each
chosen topic is verified against an actual Wikipedia article before it is queued."""
import sqlite3
from collections.abc import Callable

from autopilot import db, demand, llm, wiki

CANDIDATES_PER_SLOT = 5  # ask for more candidates than we need, so demand can pick the best

PROMPT = """Suggest {n} topics for a YouTube channel about: {niche}.
Each must be an evergreen concept, device, discovery or phenomenon that has its own Wikipedia article
(physics, chemistry, engineering, space, computing, inventions, history of science).
Do NOT suggest: medicine or health, diseases, diet, finance, law, politics, current events, or living people.
Prefer topics people genuinely wonder about. Vary the areas.
Already covered, do not repeat: {known}

For each topic also give search_query: what a curious English-speaking person would actually type into YouTube
search to learn about it. Keep it SHORT, 3-6 words, the way people really type (e.g. "why is the sky blue",
"how do mri machines work", "quantum entanglement explained"). Never a long sentence.

Return JSON: {{"topics": [{{"topic": str, "wikipedia_title": str, "search_query": str}}]}}"""


def _clean_title(title: str) -> str:
    """Models often write Wikipedia titles URL-style ("Photovoltaic_system"): underscores are spaces."""
    return " ".join(str(title).replace("_", " ").split())


def _same_article(wanted: str, found: str) -> bool:
    a, b = _clean_title(wanted).lower(), _clean_title(found).lower()
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
    score: Callable[[str], float] = demand.demand_score,
) -> list[int]:
    """Queue up to n verified, non-duplicate long-form jobs, preferring topics with real search demand."""
    known = db.known_topics(conn)
    out = gen(PROMPT.format(n=n * CANDIDATES_PER_SLOT, niche=niche, known=", ".join(sorted(known)[:80]) or "none"))
    candidates = _candidates(out)
    print(f"[topics] LLM proposed {len(candidates)} candidate(s); need {n}", flush=True)
    for c in candidates:  # demand first (cheap), Wikipedia verification only for the best (slower)
        query = str(c.get("search_query") or c.get("topic") or "").strip()
        c["_demand"] = score(query) if query else 0.0
    candidates.sort(key=lambda c: c["_demand"], reverse=True)  # stable: ties keep the model's order
    if candidates and all(c["_demand"] == 0 for c in candidates):
        print("[topics] no search-demand signal (autocomplete unreachable or nothing matched): model order", flush=True)
    added: list[int] = []
    for cand in candidates:
        topic, title = str(cand.get("topic", "")).strip(), _clean_title(cand.get("wikipedia_title", ""))
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
            try:
                src = fetch(title)
            except OSError as exc:      # Wikipedia down: skip this candidate, try the next
                print(f"[topics] could not fetch {title!r}: {exc}", flush=True)
                continue
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
        print(f"[topics] queued {topic!r} (search demand {cand['_demand']:.2f}; source: {src['title']!r}, "
              f"{len(src['text'])} chars)", flush=True)
    return added
