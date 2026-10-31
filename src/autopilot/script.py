"""Script generation. Grounded in a source article; varied by series so output is not templated."""
import random
import re
from collections.abc import Callable

from autopilot import llm

# Distinct structures keep videos from looking template-made (YouTube "inauthentic content").
SERIES = {
    "how_it_works": "Explain how it works by following one concrete example from start to finish.",
    "myth_vs_reality": "Open with the common misconception, then dismantle it step by step.",
    "origin_story": "Tell the story of how it was discovered or invented, with the key turning point.",
    "scale_and_numbers": "Build the whole video around surprising numbers and comparisons.",
    "what_if": "Pose a 'what if' question and walk through the consequences, but ONLY those the SOURCE itself describes "
               "(its mechanisms, effects and numbers). Do not invent calculations, hypothetical distances or percentages, and "
               "do not extrapolate beyond the SOURCE: if the SOURCE does not say it, leave it out.",
}

OUTLINE_PROMPT = """You are the scriptwriter for a faceless YouTube channel about {niche}.
Plan a video about: "{topic}". Style: {style}
Use ONLY facts supported by the SOURCE below. Never plan medical, financial or legal advice.

Plan exactly {n} sections. Section 1 is the COLD OPEN: its key_points are the headline answer the video will deliver (a teaser)
and ONE vivid picture or comparison, with no statistics; the numbers belong in sections 2 onward. The title keeps the topic's own
words (the topic is "{topic}") and is concrete and curiosity-driven (numbers and superlatives only if the SOURCE supports them).
The last section is the payoff. Every section has 3-5 concrete key_points taken from the SOURCE
(facts, numbers, names, mechanisms), and a short visual_query (2-4 words) for image search.

Return JSON: {{"title": str (<=70 chars), "thumbnail_text": str (<=4 words, curiosity-driven, honest),
"description": str, "tags": [str],
"sections": [{{"heading": str, "key_points": [str], "visual_query": str}}]}}

SOURCE ({source_title}):
{source_text}
"""

STYLE_RULES = """VOICE AND PACE (this is spoken aloud on YouTube; holding attention is everything):
- Talk to ONE viewer: at least one sentence in every four says "you" or "your". Sound like a sharp, funny friend who just learned something wild.
- Short, punchy sentences. Most under 12 words, none over 20. Fragments are fine. One idea per sentence.
- Concrete beats abstract: numbers, sizes, comparisons, a vivid image every few sentences.
- Ask a real question about every 60 words and answer it a few sentences later.
- Never use filler or lecture words: "furthermore", "moreover", "in conclusion", "it is important to note", "delve",
  "in this video", "let's dive in", "welcome", "today we".
- Analogies and rhetorical questions are welcome, but they must NOT introduce new facts."""

HOOK_RULE = ("- The FIRST sentence is the hook: AT MOST 12 words; a startling fact, a counter-intuitive claim or a direct "
             "question that grabs attention within 3 seconds. No throat-clearing.")

COLD_OPEN_RULE = """- THIS IS THE COLD OPEN, the part that decides whether the viewer stays past the first minute.
  Sentence 1 is the hook. Sentences 2-3 TEASE THE ANSWER this video delivers, in plain words (the most surprising thing the SOURCE says), and
  promise it will be explained. Then paint ONE vivid picture or comparison. Use AT MOST ONE number in the first 150 words: no lists of sizes,
  dates or statistics (they come later in the video)."""

COLD_WORDS, COLD_MAX_NUMBERS = 150, 2
NUM_RE = re.compile(r"\d[\d,\.]*")


def opening_numbers(text: str, words: int = COLD_WORDS) -> int:
    """How many numbers the first `words` words contain."""
    return len(NUM_RE.findall(" ".join(text.split()[:words])))


def cold_open_ok(text: str) -> bool:
    return opening_numbers(text) <= COLD_MAX_NUMBERS


COLD_PROMPT = """Rewrite the OPENING of a YouTube explainer titled "{title}" so viewers stay past the first minute.
{rule}
Keep at least {min_words} words, and use ONLY facts from the SOURCE (it is fine to drop numbers; they appear in later sections).
Short, punchy spoken sentences.

Return JSON: {{"narration": str, "claims": [str]}}  // claims: each factual claim you now make, one per item

DRAFT:
{draft}

SOURCE ({source_title}):
{source_text}
"""

RECAP_RE = re.compile(
    r"^\s*(?:you(?:'ve|’ve| have)?\s+(?:just\s+)?(?:heard|seen|saw|learned|learnt|discovered|read)\b|(?:so\s+)?now that you\b|so far\b|as we(?:'ve|’ve| have)?\s+"
    r"(?:just\s+)?(?:seen|heard|learned|discussed|covered)\b|in the (?:last|previous) section\b|before we move on\b|last time\b)", re.IGNORECASE)


def strip_recap(text: str) -> str:
    """Cut up to two opening sentences that only recap the previous section (the prompt forbids them, models still pad with them)."""
    sents = _sentences(text)
    cut = 0
    while cut < 2 and len(sents) - cut > 3 and RECAP_RE.match(sents[cut]):
        cut += 1
    return " ".join(sents[cut:]) if cut else text


SECTION_PROMPT = """You are writing one section of a narrated YouTube explainer titled "{title}".
Style: {style}
All sections, in order: {headings}

Write section {num} of {n}: "{heading}".
Cover these points, using ONLY facts in the SOURCE: {points}
{previous}
Rules:
- Write AT LEAST {words} spoken words (aim for {words}-{max_words}).
{voice}
{hook}
- {ending}
- Every sentence must be directly supported by the SOURCE. Do not add general conclusions, predictions or claims
  about significance that the SOURCE does not state; end by restating what the SOURCE established.
- Do not mention "section" or "chapter". Do not say like/subscribe. No medical, financial or legal advice.
- NEVER open by recapping the previous section ("You just heard...", "You've seen...", "Now that you know...", "So far..."). Start with something
  new: a question, a scene or the next fact.

Return JSON: {{"narration": str, "claims": [str]}}  // claims: each factual claim you made, one per item

SOURCE ({source_title}):
{source_text}
"""

SECTIONS = 6
EXCERPT_CHARS = 6000  # of the ~20,000-character article; the fact-check still reads all of it


def _tokens(text: str) -> set[str]:
    return {w for w in "".join(c.lower() if c.isalnum() else " " for c in text).split() if len(w) > 3}


def relevant_excerpt(text: str, focus: str, max_chars: int = EXCERPT_CHARS) -> str:
    """The article's opening plus the paragraphs that best match `focus`, in original order. Sending a section
    writer the whole article costs about 5,000 tokens per call, which the free tiers cannot sustain."""
    if len(text) <= max_chars:
        return text
    paras = [p for p in text.split("\n") if p.strip()]
    want, chosen, used = _tokens(focus), set(), 0
    for i in range(min(2, len(paras))):  # always keep the lead
        chosen.add(i)
        used += len(paras[i])
    ranked = sorted(range(len(paras)), key=lambda i: -len(want & _tokens(paras[i])) / (len(_tokens(paras[i])) ** 0.5 or 1))
    for i in ranked:
        if i not in chosen and used + len(paras[i]) <= max_chars:
            chosen.add(i)
            used += len(paras[i])
    return "\n".join(paras[i] for i in sorted(chosen))


def _sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]


def style_stats(text: str) -> dict:
    """How punchy a piece of narration is, in numbers (sentence length, hook length, direct address)."""
    sents = _sentences(text)
    lens = [len(s.split()) for s in sents] or [0]
    words = max(1, len(text.split()))
    return {"sentences": len(sents), "avg": sum(lens) / len(lens), "longest": max(lens),
            "long_share": sum(1 for n in lens if n > 22) / len(lens), "hook": lens[0],
            "you_per_1000": 1000 * len(re.findall(r"\b(?:you|your|you're|you'll|you've)\b", text, re.IGNORECASE)) / words}


MAX_AVG, MAX_LONG_SHARE, MAX_HOOK = 15.0, 0.15, 16


def needs_punch(text: str, first: bool) -> bool:
    s = style_stats(text)
    return s["avg"] > MAX_AVG or s["long_share"] > MAX_LONG_SHARE or (first and s["hook"] > MAX_HOOK)


PUNCH_PROMPT = """Rewrite this narration so it is punchy and fast, as it would be spoken on YouTube.
It is too long-winded: average sentence {avg:.0f} words (target under 13), longest {longest} (limit 20){hook_note}.

{style}
{hook}

HARD RULES: keep EVERY fact, number and name from the draft; add no new facts; keep at least {min_words} words.
Break long sentences into short ones. Return JSON: {{"narration": str, "claims": [str]}}
(claims: each factual claim you now make, one per item).

DRAFT:
{draft}

SOURCE ({source_title}) for checking facts:
{source_text}
"""


def _words(text: str) -> int:
    return len(text.split())


def _write_section(
    script: dict, i: int, source: dict, style: str, per: int, gen: Callable[[str], dict],
    avoid: list[str] | None = None,
) -> dict:
    """Write (or rewrite) section i. `avoid` lists claims judged unsupported by the source."""
    secs = script["sections"]
    n, sec = len(secs), secs[i]
    prev = " ".join(secs[i - 1]["narration"].split()[-30:]) if i and secs[i - 1].get("narration") else ""
    prompt = SECTION_PROMPT.format(
        title=script["title"], style=style, headings=" | ".join(s["heading"] for s in secs), num=i + 1, n=n,
        heading=sec["heading"], points="; ".join(sec.get("key_points", [])), words=per,
        max_words=round(per * 1.3), source_title=source["title"],
        source_text=relevant_excerpt(source["text"], sec["heading"] + " " + " ".join(sec.get("key_points", []))),
        previous=(f"The previous section ended with: \"{prev}\" Continue from it, without recapping it.\n" if prev
                  else "This is the opening of the video.\n"),
        voice=STYLE_RULES, hook=(HOOK_RULE + "\n" + COLD_OPEN_RULE if i == 0 else ""),
        ending=("End with a satisfying payoff that answers the opening question." if i == n - 1
                else "End with a mini open-loop that makes the viewer want the next section."),
    )
    if avoid:
        prompt += ("\nThe fact-checker judged these claims UNSUPPORTED by the SOURCE. Do not state them or anything "
                   "like them:\n" + "\n".join(f"- {c}" for c in avoid))
    out = gen(prompt)
    if _words(out.get("narration", "")) < per * 0.8:  # one targeted retry for an undershoot
        out = gen(prompt + f"\nYour last draft had only {_words(out.get('narration', ''))} words. Write at least {per}.")
    narration, claims = out.get("narration", "").strip(), out.get("claims", [])
    if narration and needs_punch(narration, first=(i == 0)):  # prompts alone drift back to long sentences: measure, fix once
        before = style_stats(narration)
        fixed = gen(PUNCH_PROMPT.format(
            avg=before["avg"], longest=before["longest"], style=STYLE_RULES, hook=(HOOK_RULE if i == 0 else ""),
            hook_note=(f"; the opening sentence is {before['hook']} words (limit 12)" if i == 0 else ""),
            min_words=round(_words(narration) * 0.85), draft=narration, source_title=source["title"],
            source_text=relevant_excerpt(source["text"], narration)))
        better = fixed.get("narration", "").strip()
        if better and style_stats(better)["avg"] < before["avg"] and _words(better) >= _words(narration) * 0.8:
            narration, claims = better, fixed.get("claims") or claims
    if narration and i == 0 and not cold_open_ok(narration):  # the opening must not be a numbers dump: rewrite it once
        fixed = gen(COLD_PROMPT.format(
            title=script["title"], rule=COLD_OPEN_RULE, min_words=round(_words(narration) * 0.8), draft=narration,
            source_title=source["title"], source_text=relevant_excerpt(source["text"], narration)))
        better = fixed.get("narration", "").strip()
        if better and cold_open_ok(better) and _words(better) >= _words(narration) * 0.7:
            narration, claims = better, fixed.get("claims") or claims
    if narration and i > 0:
        narration = strip_recap(narration)
    return {"heading": sec["heading"], "key_points": sec.get("key_points", []),
            "visual_query": sec.get("visual_query", ""), "narration": narration, "claims": claims}


def _collect_claims(script: dict) -> list[str]:
    return [c for sec in script["sections"] for c in sec.get("claims", [])]


def generate_script(
    topic: str, source: dict, niche: str, series: str | None = None, words: int = 1500,
    gen: Callable[[str], dict] = llm.generate_json, feedback: list[str] | None = None,
) -> dict:
    """Outline first, then one call per section with its own word target. A single call asked for
    1,500 words returns about 650, so length is controlled per section instead."""
    series = series or random.choice(list(SERIES))
    style = SERIES[series]
    outline_prompt = OUTLINE_PROMPT.format(
        niche=niche, topic=topic, style=style, n=SECTIONS,
        source_title=source["title"], source_text=source["text"],
    )
    if feedback:
        outline_prompt += "\nA previous attempt was rejected. Fix these problems:\n" + "\n".join(f"- {f}" for f in feedback)
    script = gen(outline_prompt)
    per = round(words / len(script["sections"]))
    for i in range(len(script["sections"])):
        script["sections"][i] = _write_section(script, i, source, style, per, gen)
        # later sections read the earlier narration for continuity, so write strictly in order
    script.update({"claims": _collect_claims(script), "series": series, "source_url": source["url"]})
    return script


def repair_sections(
    script: dict, source: dict, indexes: list[int], bad_claims: list[str],
    gen: Callable[[str], dict] = llm.generate_json,
) -> dict:
    """Rewrite only the given sections, telling the writer which claims to avoid."""
    style = SERIES.get(script.get("series", ""), "")
    for i in indexes:
        per = max(150, _words(script["sections"][i]["narration"]))
        script["sections"][i] = _write_section(script, i, source, style, per, gen, avoid=bad_claims)
    script["claims"] = _collect_claims(script)
    return script


METADATA_PROMPT = """Rewrite the YouTube title and description for a video about "{topic}".
Use ONLY facts stated in the SOURCE. Keep the title under 70 characters and the description to 2-3
sentences. Honest and curious, no exaggeration. Do not claim anything about significance, practicality or
future impact that the SOURCE does not state.
The fact-checker rejected these statements as unsupported:
{bad}

Current title: {title}
Current description: {description}

Return JSON: {{"title": str, "description": str}}

SOURCE ({source_title}):
{source_text}
"""


def repair_metadata(
    script: dict, source: dict, bad_claims: list[str], gen: Callable[[str], dict] = llm.generate_json,
) -> dict:
    out = gen(METADATA_PROMPT.format(
        topic=script.get("title", ""), bad="\n".join(f"- {c}" for c in bad_claims), title=script.get("title", ""),
        description=script.get("description", ""), source_title=source["title"], source_text=source["text"]))
    if out.get("title"):
        script["title"] = out["title"].strip()
    if out.get("description"):
        script["description"] = out["description"].strip()
    return script


TITLE_MAX = 70
SHORTEN_PROMPT = """Shorten this YouTube title to at most {max} characters. Keep the same meaning, the main keyword and the curiosity.
Do not add any new facts or claims.

Title: {title}

Return JSON: {{"title": str}}"""


def trim_title(title: str, limit: int = TITLE_MAX) -> str:
    """No-LLM fallback: drop the subtitle after a colon or dash if that fits, else cut at a word boundary."""
    for sep in (": ", " - ", " — ", " – ", "? "):
        head = title.split(sep)[0].strip()
        if sep == "? " and not head.endswith("?"):
            head += "?"
        if sep in title and 15 <= len(head) <= limit:
            return head
    return title[:limit].rsplit(" ", 1)[0].rstrip(" ,;:-—–") if len(title) > limit else title


def shorten_title(script: dict, gen: Callable[[str], dict] = llm.generate_json) -> bool:
    """Keep titles within TITLE_MAX (longer ones get cut off in search and on phones). Returns True if it changed."""
    title = script["title"].strip()
    if len(title) <= TITLE_MAX:
        return False
    try:
        new = str(gen(SHORTEN_PROMPT.format(max=TITLE_MAX, title=title)).get("title", "")).strip().strip('"')
    except (llm.LLMError, KeyError, TypeError, ValueError, AttributeError):
        new = ""
    script["title"] = new if 10 <= len(new) <= TITLE_MAX else trim_title(title)
    return True


STOP = {"what", "happens", "happen", "would", "could", "does", "when", "with", "from", "that", "this", "your", "about", "into", "have", "were",
        "will", "they", "than", "then", "them", "over", "just", "only", "like", "there", "their", "which", "while", "where", "whose", "most",
        "much", "many", "some", "really", "actually"}


def _stems(text: str) -> set[str]:
    return {w[:5] for w in re.findall(r"[a-z]{4,}", text.lower()) if w not in STOP}


def title_fits_topic(title: str, topic: str) -> bool:
    """Does the title still carry the topic's own words (a "what if Jupiter collided with Earth" video must say collided)?"""
    want = _stems(topic)
    return not want or len(want & _stems(title)) / len(want) >= 0.75


FIT_PROMPT = """A YouTube video was planned on the topic "{topic}". Its current title is "{title}", which has lost the topic's own words.
The video's sections: {headings}
Its opening: "{opening}"
Its ending: "{ending}"

1. answers_topic: does this script really answer the topic (if the topic is a question, THAT question)?
2. title: at most 70 characters, curiosity-driven, keeping the topic's key words (and its question if it is a question) AND promising
   only what the script delivers. If answers_topic is false, write the most honest title that still names the subject, without the question.

Return JSON: {{"answers_topic": bool, "title": str}}"""


def fit_title(script: dict, topic: str, gen: Callable[[str], dict] = llm.generate_json) -> str | None:
    """Make the title carry the topic's words when the script delivers on them. Returns a note if it changed the title or found that the
    script does not answer its topic (None when nothing needed doing)."""
    if title_fits_topic(script["title"], topic):
        return None
    secs = script.get("sections") or []
    try:
        out = gen(FIT_PROMPT.format(topic=topic, title=script["title"], headings=" | ".join(s["heading"] for s in secs),
                                    opening=" ".join(secs[0]["narration"].split()[:60]) if secs else "",
                                    ending=" ".join(secs[-1]["narration"].split()[-60:]) if secs else ""))
    except (llm.LLMError, KeyError, TypeError, ValueError, AttributeError):
        return None
    new = str(out.get("title", "")).strip().strip('"')
    answers = bool(out.get("answers_topic"))
    if 10 <= len(new) <= TITLE_MAX and new != script["title"]:
        old, script["title"] = script["title"], new
        return f"title {old!r} -> {new!r}" + ("" if answers else " (the script does NOT answer the topic)")
    return None if answers else "the script does NOT answer the topic"
