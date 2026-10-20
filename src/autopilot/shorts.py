"""YouTube Shorts: pick strong standalone moments from a long script and write ~45 s scripts for them."""
import re
from collections.abc import Callable
from datetime import datetime, timedelta, timezone

from autopilot import llm, qa

MIN_WORDS, MAX_WORDS = 70, 128  # ~30-55 s at the Piper voice's pace; Shorts must stay under 60 s
MAX_SECONDS = 58

PLAN_PROMPT = """Below are the narrated sections of a science explainer video titled "{title}".
Write {n} standalone YouTube Shorts scripts, each built from ONE different section.

Rules for every Short:
- {target_min}-{target_max} spoken words. This is a HARD limit: count the words. Plain, vivid, conversational.
- The first sentence is a hook: a surprising fact or a real question the Short answers. Never start with
  "In this video" or "Today".
- Use ONLY facts stated in that section. No new claims, no predictions, no advice.
- It must make sense on its own, and end on a clear payoff sentence.
- title: under 60 characters, curiosity-driven and honest.

Sections:
{sections}

Return JSON: {{"shorts": [{{"section_index": int, "title": str, "narration": str}}]}}"""

SHORTEN_PROMPT = """These YouTube Shorts scripts are too long to be read aloud in under 55 seconds.
Rewrite each so it has AT MOST {target_max} words. Keep the opening hook and the closing payoff, keep only
facts already stated in the script, and cut the least important details. Count the words.

{items}

Return JSON: {{"shorts": [{{"section_index": int, "title": str, "narration": str}}]}}"""
TARGET_MIN, TARGET_MAX = 85, 110


def _words(text: str) -> int:
    return len(text.split())


def _sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if len(s.split()) >= 3]


def trim_to_limit(narration: str, max_words: int = TARGET_MAX) -> str | None:
    """Fit a draft into max_words in code, because models cannot count: keep the hook (first sentence) and
    the payoff (last sentence), then as many middle sentences as fit, in order. None if even those two don't."""
    sents = [s for s in re.split(r"(?<=[.!?])\s+", narration.strip()) if s]
    if len(sents) < 2:
        return narration if _words(narration) <= max_words else None
    first, last, middle = sents[0], sents[-1], sents[1:-1]
    room = max_words - _words(first) - _words(last)
    if room < 0:
        return None
    kept = []
    for s in middle:
        if _words(s) <= room:
            kept.append(s)
            room -= _words(s)
    return " ".join([first, *kept, last])


def _accept(raw, n_sections: int, used: set[int]) -> tuple[list[dict], list[dict]]:
    """Split the model's output into (usable, too long). Everything else is silently invalid."""
    ok, too_long = [], []
    for s in raw.get("shorts", []) if isinstance(raw, dict) else []:
        idx, narration, title = s.get("section_index"), str(s.get("narration", "")).strip(), str(s.get("title", "")).strip()
        if not isinstance(idx, int) or not 0 <= idx < n_sections or idx in used or not title:
            continue
        item = {"section_index": idx, "title": title[:90], "narration": narration}
        if _words(narration) > MAX_WORDS:
            too_long.append(item)
        elif _words(narration) >= MIN_WORDS:
            ok.append(item)
            used.add(idx)
    return ok, too_long


def plan_shorts(
    script: dict, source: dict, n: int, gen: Callable = llm.generate_json,
) -> list[dict]:
    """Up to n fact-checked Shorts. Over-long drafts get one request to shorten; a Short with an
    unsupported sentence is dropped, not repaired: fewer Shorts is better than a wrong one."""
    sections = script["sections"]
    listing = "\n".join(f"[{i}] {s['heading']}: {s['narration']}" for i, s in enumerate(sections))
    out = gen(PLAN_PROMPT.format(title=script["title"], n=n + 1, target_min=TARGET_MIN, target_max=TARGET_MAX,
                                 sections=listing))  # ask for one extra: some will not survive
    used: set[int] = set()
    cands, too_long = _accept(out, len(sections), used)
    print(f"[shorts] model proposed {len(out.get('shorts', [])) if isinstance(out, dict) else 0}: "
          f"{len(cands)} usable, {len(too_long)} too long", flush=True)
    if too_long and len(cands) < n:
        items = "\n\n".join(f"[{c['section_index']}] {c['title']} ({_words(c['narration'])} words):\n{c['narration']}"
                            for c in too_long)
        again, still_long = _accept(gen(SHORTEN_PROMPT.format(target_max=TARGET_MAX, items=items)), len(sections), used)
        print(f"[shorts] after asking to shorten: {len(again)} usable, {len(still_long)} still too long", flush=True)
        cands += again
        too_long = still_long
    if too_long and len(cands) < n:  # the model cannot count words: trim deterministically, fact-check after
        for c in too_long:
            trimmed = trim_to_limit(c["narration"])
            if trimmed and MIN_WORDS <= _words(trimmed) <= MAX_WORDS and c["section_index"] not in used:
                cands.append({**c, "narration": trimmed})
                used.add(c["section_index"])
        print(f"[shorts] after trimming in code: {len(cands)} usable", flush=True)
    if not cands:
        return []
    claims = "\n".join(f"- [short {i}] {sent}" for i, c in enumerate(cands) for sent in _sentences(c["narration"]))
    verdict = gen(qa.FACTCHECK_PROMPT.format(source=source["text"], claims=claims))
    if verdict.get("advice_given"):
        print("[shorts] dropped all: the fact-checker saw advice", flush=True)
        return []
    bad = {int(m.group(1)) for u in verdict.get("unsupported", []) if (m := re.search(r"\[short (\d+)\]", u))}
    if verdict.get("unsupported") and not bad:  # could not tell which Short: be safe, drop them all
        print("[shorts] dropped all: unsupported claims that could not be attributed to a Short", flush=True)
        return []
    if bad:
        print(f"[shorts] dropped {len(bad)} Short(s) with unsupported claims", flush=True)
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
