"""Shot planning and image gathering for each script section.

Images are found with LLM-written specific queries, then a vision model rates each candidate
for relevance, so unrelated hits (a tin of tonic, soldiers in fog) never reach the video."""
import io
import itertools
from collections.abc import Callable
from pathlib import Path

from PIL import Image

from autopilot import commons, llm, stock

SHOT_SECONDS = 6.0
MAX_SHOTS_PER_SECTION = 16
COMMONS_CANDIDATES = 10
STOCK_CANDIDATES = 8
MIN_SCORE = 6

QUERY_PROMPT = """For a science explainer video titled "{title}" (topic: {topic}), write image search
queries for Wikimedia Commons, one set per section. Each query is 2-5 words naming a CONCRETE,
photographable or diagrammable thing (an object, device, diagram, person, place, experiment), the way a
Commons file would be titled. No abstract ideas. Give 5 varied queries per section, most specific first.

Sections:
{sections}

Also give 3 GENERIC stock-footage queries per section (1-3 words, e.g. "laboratory", "magnet", "hospital
corridor") for atmospheric b-roll that fits the topic.

Return JSON: {{"sections": [{{"queries": [str, str, str, str, str], "stock": [str, str, str]}}]}}
(same order and count)."""

RATE_PROMPT = """You are choosing footage for a section of a science explainer video.
Section: "{heading}". Narration excerpt: {excerpt}

Below are {n} candidate images, in order, with their Commons titles:
{titles}

Score each 0-10 for how well it illustrates this section. Give 0-3 to: wrong subject, logos,
slides/posters full of text, unrelated people or scenes. Give 8-10 only to clearly on-topic, clean,
good-looking images. Return JSON: {{"scores": [int, ...]}} with exactly {n} integers."""


def plan_shots(timings: list[dict], fps: int = 24) -> list[list[tuple[int, int]]]:
    """Per section, a list of (start_frame, end_frame) spans. Boundaries come from cumulative
    rounding, so total frames match the narration exactly and nothing drifts."""
    plan = []
    for sec in timings:
        n = max(1, min(MAX_SHOTS_PER_SECTION, round((sec["end"] - sec["start"]) / SHOT_SECONDS)))
        edges = [round((sec["start"] + (sec["end"] - sec["start"]) * i / n) * fps) for i in range(n + 1)]
        plan.append(list(itertools.pairwise(edges)))
    return plan


def plan_queries(script: dict, topic: str, gen: Callable = llm.generate_json) -> list[dict]:
    """One LLM call for all sections -> [{"commons": [...], "stock": [...]}]. Falls back on any failure."""
    secs = script["sections"]
    fallback = [{
        "commons": [s.get("visual_query") or s["heading"], f"{s['heading']} {topic}", topic],
        "stock": [s.get("visual_query") or topic, topic],
    } for s in secs]
    listing = "\n".join(f"{i + 1}. {s['heading']}: {s['narration'][:220]}" for i, s in enumerate(secs))
    try:
        out = gen(QUERY_PROMPT.format(title=script["title"], topic=topic, sections=listing))
        planned = [
            {"commons": list(map(str, s["queries"])), "stock": list(map(str, s.get("stock", [])))}
            for s in out["sections"]
        ]
    except (llm.LLMError, KeyError, TypeError):
        return fallback
    if len(planned) != len(secs):
        return fallback
    return [{"commons": p["commons"] + fb["commons"], "stock": p["stock"] + fb["stock"]}
            for p, fb in zip(planned, fallback)]  # LLM queries first, fallbacks as backup


def _jpeg_small(path: Path, side: int = 512) -> bytes:
    img = Image.open(path).convert("RGB")
    img.thumbnail((side, side))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=70)
    return buf.getvalue()


def rate_candidates(section: dict, paths: list[Path], titles: list[str], gen: Callable = llm.generate_json) -> list[int]:
    """Vision-rate candidates; on failure return neutral scores so the pipeline still runs."""
    prompt = RATE_PROMPT.format(
        heading=section["heading"], excerpt=section["narration"][:400], n=len(paths),
        titles="\n".join(f"{i + 1}. {t}" for i, t in enumerate(titles)),
    )
    try:
        scores = gen(prompt, images=[_jpeg_small(p) for p in paths])["scores"]
        if len(scores) == len(paths):
            return [int(s) for s in scores]
    except (llm.LLMError, KeyError, TypeError, ValueError):
        pass
    return [MIN_SCORE] * len(paths)


def _interleave(items: list[dict]) -> list[dict]:
    """Alternate stills and video so consecutive shots don't feel samey."""
    imgs = [i for i in items if i["kind"] == "image"]
    vids = [i for i in items if i["kind"] == "video"]
    out = []
    while imgs or vids:
        for pool in (imgs, vids):
            if pool:
                out.append(pool.pop(0))
    return out


def _search_pool(queries: list[str], search: Callable, limit: int, seen: set[str]) -> list[dict]:
    pool: list[dict] = []
    for q in queries:
        try:
            results = search(q)
        except OSError:
            continue
        for item in results:
            key = item["thumb"]
            if key not in seen and all(key != c["thumb"] for c in pool):
                pool.append(item)
        if len(pool) >= limit:
            break
    return pool[:limit]


def gather_images(
    script: dict, plan: list, cache: Path, topic: str, gen: Callable = llm.generate_json,
) -> tuple[list[list[dict]], list[str]]:
    """Return (items per section, credit lines). Each item is {"kind": "image"|"video", "path": Path}.
    A section with no items gets [] (title-card fallback)."""
    queries = plan_queries(script, topic, gen)
    seen: set[str] = set()
    credits: list[str] = []
    per_section: list[list[dict]] = []
    for section, spans, qs in zip(script["sections"], plan, queries):
        pool = (_search_pool(qs["commons"], commons.search, COMMONS_CANDIDATES, seen)
                + _search_pool(qs["stock"], stock.search, STOCK_CANDIDATES, seen))
        files, ok = [], []
        for item in pool:
            try:
                grab = commons.download if item["kind"] == "image" else stock.download_thumb
                files.append(grab(item, cache))
                ok.append(item)
            except OSError:
                continue
        scores = rate_candidates(section, files, [c["title"] for c in ok], gen) if files else []
        ranked = sorted(zip(scores, range(len(ok))), reverse=True)
        keep = [ok[i] for s, i in ranked if s >= MIN_SCORE][:len(spans)]
        chosen = []
        for item in _interleave(keep):
            try:
                path = files[ok.index(item)] if item["kind"] == "image" else stock.download_video(item, cache)
            except OSError:
                continue
            seen.add(item["thumb"])
            line = commons.credit_line(item) if item["kind"] == "image" else stock.credit_line(item)
            credits.append(line)
            chosen.append({"kind": item["kind"], "path": path})
        per_section.append(chosen)
    return per_section, credits
