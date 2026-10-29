"""Topic discovery: the LLM brainstorms evergreen questions, real search demand ranks them, and each
chosen topic is verified against an actual Wikipedia article before it is queued."""
import sqlite3
from collections.abc import Callable

from autopilot import db, demand, llm, wiki

CANDIDATES_PER_SLOT = 5  # ask for more candidates than we need, so demand can pick the best

CATEGORIES = {
    "core": "evergreen science and technology: how everyday devices and big ideas work (physics, chemistry, engineering, "
            "computing, inventions)",
    "space": "space and astronomy: planets, moons, stars, galaxies, black holes, telescopes, space missions and spaceflight history",
    "what_if": "'what if' science: a vivid question about a real phenomenon whose answer follows from established science "
               "(for example what would happen to the tides if the Moon were gone). The topic is the question; the "
               "Wikipedia article is the science behind it",
    "history": "history mysteries and the history of science: documented puzzles, enigmatic discoveries, lost knowledge, "
               "famous experiments and long-running debates (NOT crimes or victims, NOT living people)",
}
SERIES_FOR = {"what_if": ["what_if"], "history": ["origin_story", "myth_vs_reality"],
              "space": ["how_it_works", "scale_and_numbers", "origin_story"]}

PROMPT = """Suggest {n} topics for a YouTube channel about: {niche}.
This batch of topics must be about: {focus}.
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


def pick_category(conn: sqlite3.Connection, mix: dict[str, float], window: int = 8, avoid: set[str] | None = None) -> str:
    """The category furthest below its target share among the last `window` long videos (jobs made before categories existed
    count as core). With no mix configured every topic is core."""
    mix = {k: v for k, v in (mix or {}).items() if k in CATEGORIES and v > 0} or {"core": 1.0}
    if avoid and len(set(mix) - avoid) >= 1:        # a category whose script just failed is skipped for the replacement topic
        mix = {k: v for k, v in mix.items() if k not in avoid}
    rows = conn.execute("SELECT category FROM jobs WHERE kind = 'long' AND status != 'failed' ORDER BY id DESC LIMIT ?",
                        (window,)).fetchall()
    counts = {k: 0 for k in mix}
    for r in rows:
        counts[r["category"] if r["category"] in counts else "core" if "core" in counts else next(iter(counts))] += 1
    total = sum(mix.values())
    n = max(1, len(rows))
    return max(mix, key=lambda k: (mix[k] / total - counts[k] / n, mix[k]))


def series_for(category: str | None) -> str | None:
    """The script style that suits a category (None: any, as before)."""
    import random

    options = SERIES_FOR.get(category or "")
    return random.choice(options) if options else None


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


def discover_mix(conn: sqlite3.Connection, niche: str, n: int, mix: dict[str, float], avoid: set[str] | None = None,
                 **kwargs) -> list[int]:
    """Queue n topics, one slot at a time, each from the category the mix says is due next."""
    ids: list[int] = []
    for _ in range(n):
        cat = pick_category(conn, mix, avoid=avoid)
        print(f"[topics] next category: {cat}", flush=True)
        ids += discover(conn, niche, 1, category=cat, **kwargs)
    return ids


def discover(
    conn: sqlite3.Connection, niche: str, n: int, gen: Callable = llm.generate_json,
    fetch: Callable = wiki.fetch_source, forbidden: list[str] | None = None, min_source_chars: int = 2500,
    score: Callable[[str], float] = demand.demand_score, category: str = "core",
) -> list[int]:
    """Queue up to n verified, non-duplicate long-form jobs, preferring topics with real search demand."""
    known = db.known_topics(conn)
    out = gen(PROMPT.format(n=n * CANDIDATES_PER_SLOT, niche=niche, focus=CATEGORIES.get(category, CATEGORIES["core"]),
                            known=", ".join(sorted(known)[:80]) or "none"))
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
        added.append(db.add_job(conn, topic, "long", src["title"], category=category))
        print(f"[topics] queued [{category}] {topic!r} (search demand {cand['_demand']:.2f}; source: {src['title']!r}, "
              f"{len(src['text'])} chars)", flush=True)
    return added
