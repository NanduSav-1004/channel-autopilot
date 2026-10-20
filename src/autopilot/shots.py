"""Shot planning and image gathering for each script section."""
import itertools
from pathlib import Path

from autopilot import commons

SHOT_SECONDS = 6.0
MAX_SHOTS_PER_SECTION = 16


def plan_shots(timings: list[dict], fps: int = 24) -> list[list[tuple[int, int]]]:
    """Per section, a list of (start_frame, end_frame) spans. Boundaries come from cumulative
    rounding, so total frames match the narration exactly and nothing drifts."""
    plan = []
    for sec in timings:
        n = max(1, min(MAX_SHOTS_PER_SECTION, round((sec["end"] - sec["start"]) / SHOT_SECONDS)))
        edges = [round((sec["start"] + (sec["end"] - sec["start"]) * i / n) * fps) for i in range(n + 1)]
        plan.append(list(itertools.pairwise(edges)))
    return plan


def gather_images(script: dict, plan: list, cache: Path, topic: str) -> tuple[list[list[Path]], list[str]]:
    """Return (images per section, credit lines). A section with no images gets [] (title-card fallback)."""
    used: set[str] = set()
    credits: list[str] = []
    per_section: list[list[Path]] = []
    for section, spans in zip(script["sections"], plan):
        need = len(spans)
        queries = [section.get("visual_query", ""), f"{section['heading']} {topic}", topic]
        found: list[dict] = []
        for q in filter(None, queries):
            try:
                results = commons.search(q)
            except OSError:
                continue
            for item in results:
                if item["thumb"] not in used and item not in found:
                    found.append(item)
            if len(found) >= need:
                break
        found = found[:need]
        paths = []
        for item in found:
            try:
                paths.append(commons.download(item, cache))
            except OSError:
                continue
            used.add(item["thumb"])
            credits.append(commons.credit_line(item))
        per_section.append(paths)
    return per_section, credits
