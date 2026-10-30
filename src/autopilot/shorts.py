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
- The first sentence is a hook of AT MOST 10 words: a surprising fact or a real question the Short answers.
  Never start with "In this video" or "Today".
- Talk to ONE viewer ("you"). Short punchy sentences, most under 12 words. No filler words.
- Use ONLY the verified facts listed for that section. Do NOT add evaluations, significance, predictions or
  superlatives ("the only way", "fundamentally changes", "revolutionary"). State what is known and stop.
- No advice.
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
REPAIR_PROMPT = """These YouTube Shorts scripts each contain sentences that a fact-checker could NOT support from the SOURCE.
Rewrite each script: replace every flagged sentence with one that states only what the SOURCE says, or delete the sentence if the
SOURCE has nothing to say about it. Keep the opening hook first and a clear payoff sentence last; keep the script between
{target_min} and {target_max} words; add no new facts, numbers or superlatives. Keep each script's section_index and title.

{items}

SOURCE:
{source}

Return JSON: {{"shorts": [{{"section_index": int, "title": str, "narration": str}}]}}"""
REPAIR_ROUNDS = 2
TARGET_MIN, TARGET_MAX = 85, 110


def _words(text: str) -> int:
    return len(text.split())


def _sentences(text: str) -> list[str]:
    """The sentences worth fact-checking: statements. A question asserts nothing, so it is never a claim."""
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if len(s.split()) >= 3 and not s.rstrip().endswith("?")]


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


def attribute_unsupported(unsupported: list[str], cands: list[dict]) -> tuple[set[int], list[str]]:
    """Map each rejected sentence to the Short it came from: by its [short N] tag when present, otherwise
    by word overlap (the fact-checker often paraphrases). Returns (bad Short indexes, unattributable)."""
    bad: set[int] = set()
    unknown: list[str] = []
    for u in unsupported:
        u = str(u)
        m = re.search(r"\[short (\d+)\]", u)
        if m and int(m.group(1)) < len(cands):
            bad.add(int(m.group(1)))
            continue
        ut = qa._tokens(re.sub(r"\[short \d+\]", "", u))
        scores = [len(ut & qa._tokens(c["narration"])) / (len(ut) or 1) for c in cands]
        best = max(range(len(cands)), key=scores.__getitem__) if cands else None
        if best is not None and scores[best] >= 0.5:
            bad.add(best)
        else:
            unknown.append(u)
    return bad, unknown


def attribute_each(unsupported: list[str], cands: list[dict]) -> tuple[dict[int, list[str]], list[str]]:
    """Like attribute_unsupported, but keeps WHICH sentences were rejected for each Short: {short index: [sentences]}."""
    per: dict[int, list[str]] = {}
    unknown: list[str] = []
    for u in unsupported:
        u = str(u)
        idxs, _ = attribute_unsupported([u], cands)
        if idxs:
            per.setdefault(next(iter(idxs)), []).append(re.sub(r"^\[short \d+\]\s*", "", u))
        else:
            unknown.append(u)
    return per, unknown


def _check(cands: list[dict], source: dict, gen: Callable) -> tuple[dict[int, list[str]], list[str], bool]:
    """Fact-check the Shorts' statements: (rejected sentences per Short, unattributable ones, advice flag)."""
    claims = "\n".join(f"- [short {i}] {sent}" for i, c in enumerate(cands) for sent in _sentences(c["narration"]))
    if not claims:
        return {}, [], False
    verdict = gen(qa.FACTCHECK_PROMPT.format(source=source["text"], claims=claims))
    per, unknown = attribute_each(verdict.get("unsupported", []), cands)
    return per, unknown, bool(verdict.get("advice_given"))


def repair_shorts(cands: list[dict], per: dict[int, list[str]], source: dict, gen: Callable) -> dict[int, dict]:
    """One request to rewrite the Shorts that have unsupported sentences. Returns {index in cands: repaired candidate}."""
    items = "\n\n".join(
        f"[{cands[i]['section_index']}] {cands[i]['title']}:\n{cands[i]['narration']}\nFLAGGED:\n" + "\n".join(f"- {s}" for s in per[i])
        for i in sorted(per))
    out = gen(REPAIR_PROMPT.format(target_min=TARGET_MIN, target_max=TARGET_MAX, items=items, source=source["text"]))
    by_section = {c["section_index"]: i for i, c in enumerate(cands)}
    fixed: dict[int, dict] = {}
    for s in out.get("shorts", []) if isinstance(out, dict) else []:
        i = by_section.get(s.get("section_index"))
        narration = str(s.get("narration", "")).strip()
        if i is None or i not in per:
            continue
        if _words(narration) > MAX_WORDS:
            narration = trim_to_limit(narration) or ""
        if MIN_WORDS <= _words(narration) <= MAX_WORDS:
            fixed[i] = {**cands[i], "narration": narration}
    return fixed


def plan_shorts(
    script: dict, source: dict, n: int, gen: Callable = llm.generate_json, exclude: set[int] | None = None,
) -> list[dict]:
    """Up to n fact-checked Shorts. Over-long drafts get one request to shorten; a Short with an
    unsupported sentence is dropped, not repaired: fewer Shorts is better than a wrong one."""
    sections = script["sections"]
    listing = "\n".join(
        f"[{i}] {s['heading']}: {s['narration']}"
        + (f"\n    Verified facts: {' | '.join(s['claims'])}" if s.get("claims") else "")
        for i, s in enumerate(sections))
    out = gen(PLAN_PROMPT.format(title=script["title"], n=n * 2, target_min=TARGET_MIN, target_max=TARGET_MAX,
                                 sections=listing))  # ask for twice as many: the length and fact-check filters drop some
    used: set[int] = set(exclude or ())          # sections that already have a Short are not offered again
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
    per, unknown, advice = _check(cands, source, gen)
    if advice:
        print("[shorts] dropped all: the fact-checker saw advice", flush=True)
        return []
    if unknown:  # a rejected sentence that matches no Short: be safe and drop them all
        print(f"[shorts] dropped all: could not attribute {len(unknown)} unsupported claim(s), e.g.: "
              f"{'; '.join(u[:120] for u in unknown[:3])}", flush=True)
        return []
    dropped = 0
    for rnd in range(REPAIR_ROUNDS):          # a Short with an unsupported sentence is rewritten from the source, then re-checked
        if not per:
            break
        print(f"[shorts] repairing {len(per)} Short(s) with unsupported sentences, e.g.: "
              f"{'; '.join(s[:100] for v in list(per.values())[:2] for s in v[:1])}", flush=True)
        fixed = repair_shorts(cands, per, source, gen)
        for i in per:
            if i not in fixed:
                cands[i]["_bad"] = True         # the model gave nothing usable back: this one goes
                dropped += 1
            else:
                cands[i] = fixed[i]
        cands = [c for c in cands if not c.get("_bad")]
        if not cands:
            break
        if not fixed:                          # nothing was rewritten: the rest passed the first check
            per = {}
            break
        per, unknown, advice = _check(cands, source, gen)
        if advice or unknown:
            print("[shorts] dropped all after repair: advice or unattributable claims", flush=True)
            return []
    if per:                                   # still unsupported after the repair rounds
        cands = [c for i, c in enumerate(cands) if i not in per]
        dropped += len(per)
    if dropped:
        print(f"[shorts] dropped {dropped} Short(s) that could not be repaired", flush=True)
    return cands[:n]


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


def _plain_title(heading: str) -> str:
    title = re.sub(r"^(Hook|Payoff|Foundations|Intro|Conclusion)\s*[:\u2013\u2014-]\s*", "", heading.strip(), flags=re.IGNORECASE)
    return (title[:57].rsplit(" ", 1)[0] + "...") if len(title) > 60 else title


def extractive_shorts(script: dict, n: int, exclude: set[int] | None = None) -> list[dict]:
    """The last resort that makes "n Shorts a day" a rule: a Short made only of sentences taken VERBATIM from one section of the long
    script. That script already passed the fact-check, so nothing new needs checking. The hook (first sentence) and payoff (last
    sentence) are kept, with as many middle sentences as fit. Less punchy than a rewritten Short, but never wrong and never missing."""
    out: list[dict] = []
    for i, sec in enumerate(script.get("sections", [])):
        if i in (exclude or set()):
            continue
        text = trim_to_limit(sec["narration"], TARGET_MAX)
        if text and MIN_WORDS <= _words(text) <= MAX_WORDS:
            out.append({"section_index": i, "title": _plain_title(sec["heading"]), "narration": text})
    out.sort(key=lambda s: -_words(s["narration"]))      # the fuller sections make the better Shorts
    return sorted(out[:n], key=lambda s: s["section_index"])


def plan_shorts_strict(script: dict, source: dict, n: int, gen: Callable = llm.generate_json, log: Callable[[str], None] = print,
                       have: list[dict] | None = None) -> list[dict]:
    """Exactly n Shorts whenever the script has enough sections: first the normal planner, then a second planning round for what is
    missing, then verbatim extracts from the long script. `have` = Shorts that already exist (their sections are not reused)."""
    have = list(have or [])
    got: list[dict] = []
    for attempt in range(2):
        need = n - len(have) - len(got)
        if need <= 0:
            break
        try:
            got += plan_shorts(script, source, need, gen, exclude={s["section_index"] for s in have + got})
        except (llm.LLMError, KeyError, TypeError, ValueError) as exc:
            log(f"[shorts] planning round {attempt + 1} failed ({type(exc).__name__}); trying again")
    need = n - len(have) - len(got)
    if need > 0:
        extra = extractive_shorts(script, need, {s["section_index"] for s in have + got})
        log(f"[shorts] only {len(got)} rewritten Short(s) passed; adding {len(extra)} made of the long script's own sentences")
        got += extra
    return got[:max(0, n - len(have))]
