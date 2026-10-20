"""YouTube Shorts: pick strong standalone moments from a long script and write ~45 s scripts for them."""
import re
from collections.abc import Callable
from datetime import datetime, timedelta, timezone

from autopilot import llm, qa

MIN_WORDS, MAX_WORDS = 70, 130  # ~30-55 s at the Piper voice's pace; Shorts must stay under 60 s
MAX_SECONDS = 58

PLAN_PROMPT = """Below are the narrated sections of a science explainer video titled "{title}".
Write {n} standalone YouTube Shorts scripts, each built from ONE different section.

Rules for every Short:
- {min_words}-{max_words} spoken words. Plain, vivid, conversational.
- The first sentence is a hook: a surprising fact or a real question the Short answers. Never start with
  "In this video" or "Today".
- Use ONLY facts stated in that section. No new claims, no predictions, no advice.
- It must make sense on its own, and end on a clear payoff sentence.
- title: under 60 characters, curiosity-driven and honest.

Sections:
{sections}

Return JSON: {{"shorts": [{{"section_index": int, "title": str, "narration": str}}]}}"""


def _words(text: str) -> int:
    return len(text.split())


def _sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if len(s.split()) >= 3]


def plan_shorts(
    script: dict, source: dict, n: int, gen: Callable = llm.generate_json,
) -> list[dict]:
    """Up to n fact-checked Shorts. A Short with an unsupported sentence is dropped, not repaired:
    fewer Shorts is better than a wrong one."""
    sections = script["sections"]
    listing = "\n".join(f"[{i}] {s['heading']}: {s['narration']}" for i, s in enumerate(sections))
    out = gen(PLAN_PROMPT.format(title=script["title"], n=n + 1, min_words=MIN_WORDS, max_words=MAX_WORDS,
                                 sections=listing))  # ask for one extra: some will not survive
    cands, used = [], set()
    for s in out.get("shorts", []) if isinstance(out, dict) else []:
        idx, narration, title = s.get("section_index"), str(s.get("narration", "")).strip(), str(s.get("title", "")).strip()
        if not isinstance(idx, int) or not 0 <= idx < len(sections) or idx in used or not title:
            continue
        if not MIN_WORDS <= _words(narration) <= MAX_WORDS:
            continue
        used.add(idx)
        cands.append({"section_index": idx, "title": title[:90], "narration": narration})
    if not cands:
        return []
    claims = "\n".join(f"- [short {i}] {sent}" for i, c in enumerate(cands) for sent in _sentences(c["narration"]))
    verdict = gen(qa.FACTCHECK_PROMPT.format(source=source["text"], claims=claims))
    if verdict.get("advice_given"):
        return []
    bad = {int(m.group(1)) for u in verdict.get("unsupported", []) if (m := re.search(r"\[short (\d+)\]", u))}
    if verdict.get("unsupported") and not bad:  # could not tell which Short: be safe, drop them all
        return []
    return [c for i, c in enumerate(cands) if i not in bad][:n]


def caption_chunks(sentences: list[dict], max_words: int = 6) -> list[tuple[str, float, float]]:
    """Split timed sentences into short on-screen chunks, timed in proportion to word count."""
    chunks = []
    for s in sentences:
        words = s["text"].split()
        groups = [words[i:i + max_words] for i in range(0, len(words), max_words)] or [[]]
        if len(groups) > 1 and len(groups[-1]) <= 2:  # avoid a one- or two-word orphan
            tail = groups.pop()
            groups[-1] += tail
        total, t = max(1, sum(len(g) for g in groups)), s["start"]
        span = s["end"] - s["start"]
        for g in groups:
            end = t + span * len(g) / total
            chunks.append((" ".join(g), t, end))
            t = end
    return chunks


def publish_times(count: int, offsets_hours: list[float], now: datetime | None = None) -> list[str]:
    """RFC 3339 UTC times to spread Shorts through the day instead of posting them together."""
    now = now or datetime.now(timezone.utc)
    return [(now + timedelta(hours=offsets_hours[i % len(offsets_hours)] + 12 * (i // len(offsets_hours))))
            .strftime("%Y-%m-%dT%H:%M:%SZ") for i in range(count)]


def short_description(hook: str, parent_video_id: str | None, source_url: str | None, credits: list[str]) -> str:
    parts = [hook.strip()]
    if parent_video_id:
        parts.append(f"Watch the full video: https://youtu.be/{parent_video_id}")
    if source_url:
        parts.append(f"Source: {source_url}")
    parts.append("This video uses AI-assisted scripting and a synthetic voice.")
    text = "\n\n".join(p for p in parts if p)
    if credits:
        header, kept, room = "\n\nImage and video credits:\n", [], 4800 - len(text) - 60
        for i, line in enumerate(credits):
            if len(line) + 1 > room:
                kept.append(f"...and {len(credits) - i} more (see the full video)")
                break
            kept.append(line)
            room -= len(line) + 1
        text += header + "\n".join(kept)
    return text[:5000]
