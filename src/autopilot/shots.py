"""Shot planning and image gathering for each script section.

Images are found with LLM-written specific queries, then a vision model rates each candidate
for relevance, so unrelated hits (a tin of tonic, soldiers in fog) never reach the video."""
import io
import itertools
from collections.abc import Callable
from pathlib import Path

from PIL import Image

from autopilot import commons, llm, nasa, stock

SHOT_SECONDS = 6.0          # how much media to GATHER: about one distinct image per this many seconds
CUT_SECONDS = 3.5           # how often a long video CUTS to a new shot
SHORT_CUT_SECONDS = 2.6     # and a Short
MAX_REUSE = 3               # an image or clip may appear this many times, each time showing a different part of it
SHORT_MAX_REUSE = 3         # a Short is short enough to allow one more
MAX_SHOTS_PER_SECTION = 40
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

RATE_PROMPT = """You are choosing footage for sections of a science explainer video.
Below are {n} candidate images/video thumbnails, numbered 1..{n} in the order attached, grouped by section.

{groups}

Score every candidate 0-10 for how well it illustrates ITS OWN section. Give 0-3 to: wrong subject, logos,
slides/posters full of text, unrelated people or scenes. Give 8-10 only to clearly on-topic, clean,
good-looking images. Return JSON: {{"scores": [int, ...]}} with exactly {n} integers, in order."""
SECTIONS_PER_RATING_CALL = 4  # one vision request covers several sections to save free-tier quota


def plan_cuts(
    timings: list[dict], media_counts: list[int], fps: int = 24, cut_seconds: float = CUT_SECONDS,
    max_reuse: int = MAX_REUSE,
) -> list[list[tuple[int, int]]]:
    """Frame spans per section for the RENDER: cut every `cut_seconds`, but never use a piece of media more than
    `max_reuse` times. A section with little media therefore cuts more slowly, and one with none (title card) slowly."""
    plan = []
    for sec, have in zip(timings, media_counts, strict=True):
        dur = sec["end"] - sec["start"]
        want = round(dur / cut_seconds) if have else round(dur / SHOT_SECONDS)
        n = max(1, min(MAX_SHOTS_PER_SECTION, want, max_reuse * have if have else want))
        edges = [round((sec["start"] + dur * k / n) * fps) for k in range(n + 1)]
        plan.append(list(itertools.pairwise(edges)))
    return plan


def cut_choice(k: int, pool_size: int) -> tuple[int, int, int]:
    """For the k-th shot of a section drawing on `pool_size` media: (which media, how many times it has been used
    before, which camera move). The move differs between the first and the second use of the same media."""
    item, cycle = k % pool_size, k // pool_size
    return item, cycle, (item + cycle) % 3


def plan_shots(
    timings: list[dict], fps: int = 24, shot_seconds: float = SHOT_SECONDS,
) -> list[list[tuple[int, int]]]:
    """Per section, a list of (start_frame, end_frame) spans. Boundaries come from cumulative
    rounding, so total frames match the narration exactly and nothing drifts."""
    plan = []
    for sec in timings:
        n = max(1, min(MAX_SHOTS_PER_SECTION, round((sec["end"] - sec["start"]) / shot_seconds)))
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


def rate_sections(
    groups: list[tuple[dict, list[Path], list[str]]], gen: Callable = llm.generate_json,
) -> list[list[int]]:
    """groups: [(section, image files, titles)]. One vision call per SECTIONS_PER_RATING_CALL sections.
    Returns scores per group; on failure falls back to neutral scores so the pipeline still runs."""
    out: list[list[int]] = []
    for i in range(0, len(groups), SECTIONS_PER_RATING_CALL):
        batch = groups[i:i + SECTIONS_PER_RATING_CALL]
        files = [f for _, fs, _ in batch for f in fs]
        if not files:
            out += [[] for _ in batch]
            continue
        lines, k = [], 1
        for sec, fs, titles in batch:
            lines.append(f'SECTION "{sec["heading"]}": {sec["narration"][:250]}')
            for title in titles:
                lines.append(f"  {k}. {title}")
                k += 1
        scores = None
        try:
            scores = gen(RATE_PROMPT.format(n=len(files), groups="\n".join(lines)),
                         images=[_jpeg_small(f, 448) for f in files])["scores"]
        except (llm.LLMError, KeyError, TypeError, ValueError):
            pass
        if not scores or len(scores) != len(files):
            scores = [MIN_SCORE] * len(files)
        pos = 0
        for _, fs, _ in batch:
            out.append([int(s) for s in scores[pos:pos + len(fs)]])
            pos += len(fs)
    return out


def best_first(scores: list[int]) -> list[int]:
    """Candidate indexes, best score first. On a tie (for example the rating was unavailable and every score is neutral)
    the EARLIER candidate wins: it came from the most specific search query."""
    return sorted(range(len(scores)), key=lambda i: (-scores[i], i))


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


NASA_CANDIDATES = 8


def _thumb(item: dict, cache: Path) -> Path:
    if item.get("source") == "nasa":
        return nasa.download_thumb(item, cache)
    return commons.download(item, cache) if item["kind"] == "image" else stock.download_thumb(item, cache)


def gather_images(
    script: dict, plan: list, cache: Path, topic: str, gen: Callable = llm.generate_json, use_nasa: bool = False,
) -> tuple[list[list[dict]], list[str]]:
    """Return (items per section, credit lines). Each item is {"kind": "image"|"video", "path": Path}.
    A section with no items gets [] (title-card fallback)."""
    queries = plan_queries(script, topic, gen)
    seen: set[str] = set()
    pools: list[tuple[list[dict], list[Path]]] = []
    for qs in queries:
        pool = (_search_pool(qs["commons"], commons.search, COMMONS_CANDIDATES, seen)
                + _search_pool(qs["stock"], stock.search, STOCK_CANDIDATES, seen))
        if use_nasa:       # space topics: NASA's public-domain pictures and footage, found with the same specific queries
            pool += (_search_pool(qs["commons"], nasa.search_images, NASA_CANDIDATES, seen)
                     + _search_pool(qs["commons"], nasa.search_videos, 3, seen))
        files, ok = [], []
        for item in pool:
            try:
                files.append(_thumb(item, cache))
                ok.append(item)
            except OSError:
                continue
        pools.append((ok, files))
        seen |= {c["thumb"] for c in ok}  # a candidate is only offered to one section

    scores = rate_sections(
        [(sec, files, [c["title"] for c in ok]) for sec, (ok, files) in zip(script["sections"], pools)], gen)

    credits: list[str] = []
    per_section: list[list[dict]] = []
    for (ok, files), sc, spans in zip(pools, scores, plan):
        keep = [ok[i] for i in best_first(sc) if sc[i] >= MIN_SCORE][:len(spans)]
        chosen = []
        for item in _interleave(keep):
            try:
                if item.get("source") == "nasa":
                    path = nasa.download_image(item, cache) if item["kind"] == "image" else nasa.download_video(item, cache)
                else:
                    path = files[ok.index(item)] if item["kind"] == "image" else stock.download_video(item, cache)
            except OSError:
                continue
            credits.append(nasa.credit_line(item) if item.get("source") == "nasa" else
                           commons.credit_line(item) if item["kind"] == "image" else stock.credit_line(item))
            chosen.append({"kind": item["kind"], "path": path})
        per_section.append(chosen)
    return per_section, credits


def short_media_pool(sections: list[list[dict]], idx: int, want: int = 8) -> list[dict]:
    """Media for a Short cut from section `idx`: that section's own, then its nearest neighbours' (same video, so on
    topic) until there is enough to cut quickly without repeating."""
    order = [idx] + [j for _, j in sorted((abs(j - idx), j) for j in range(len(sections)) if j != idx)]
    pool: list[dict] = []
    for j in order:
        pool += sections[j]
        if len(pool) >= want:
            break
    return pool


MIN_SECTION_MEDIA = 5


def fill_sparse_sections(sections: list[list[dict]], min_items: int = MIN_SECTION_MEDIA) -> list[list[dict]]:
    """A section that found little media would hold on a couple of pictures for 20+ seconds. Let it borrow from its
    nearest neighbours (same video, so on topic). Borrowed items are marked so the renderer shows them from a
    different angle than where they appear in their own section."""
    out = []
    for i, own in enumerate(sections):
        pool = list(own)
        if len(pool) < min_items:
            for j in [j for _, j in sorted((abs(j - i), j) for j in range(len(sections)) if j != i)]:
                pool += [{**m, "borrowed": True} for m in sections[j]]
                if len(pool) >= min_items:
                    break
        out.append(pool)
    return out


def estimate_timings(script: dict) -> list[dict]:
    """Rough section timings from the narration length (only used to decide how much media to look for)."""
    t, out = 0.0, []
    for sec in script["sections"]:
        d = max(20.0, len(sec["narration"].split()) * 0.5)
        out.append({"heading": sec["heading"], "start": t, "end": t + d, "sentences": []})
        t += d
    return out


def recover_items(script: dict, topic: str, cache: Path, use_nasa: bool = False, gen: Callable = llm.generate_json):
    """Find media again for a finished video whose media is gone (a later run on a fresh machine). Returns (items, credits)."""
    plan = plan_shots(estimate_timings(script))
    return gather_images(script, plan, cache, topic, gen=gen, use_nasa=use_nasa)
