"""Script generation. Grounded in a source article; varied by series so output is not templated."""
import random
from collections.abc import Callable

from autopilot import llm

# Distinct structures keep videos from looking template-made (YouTube "inauthentic content").
SERIES = {
    "how_it_works": "Explain how it works by following one concrete example from start to finish.",
    "myth_vs_reality": "Open with the common misconception, then dismantle it step by step.",
    "origin_story": "Tell the story of how it was discovered or invented, with the key turning point.",
    "scale_and_numbers": "Build the whole video around surprising numbers and comparisons.",
    "what_if": "Pose a 'what if' question and reason through the consequences using real science.",
}

OUTLINE_PROMPT = """You are the scriptwriter for a faceless YouTube channel about {niche}.
Plan a video about: "{topic}". Style: {style}
Use ONLY facts supported by the SOURCE below. Never plan medical, financial or legal advice.

Plan exactly {n} sections. Section 1 is the hook: it opens with a real question the video answers.
The last section is the payoff. Every section has 3-5 concrete key_points taken from the SOURCE
(facts, numbers, names, mechanisms), and a short visual_query (2-4 words) for image search.

Return JSON: {{"title": str (<=70 chars), "thumbnail_text": str (<=4 words, curiosity-driven, honest),
"description": str, "tags": [str],
"sections": [{{"heading": str, "key_points": [str], "visual_query": str}}]}}

SOURCE ({source_title}):
{source_text}
"""

SECTION_PROMPT = """You are writing one section of a narrated YouTube explainer titled "{title}".
Style: {style}
All sections, in order: {headings}

Write section {num} of {n}: "{heading}".
Cover these points, using ONLY facts in the SOURCE: {points}
{previous}
Rules:
- Write AT LEAST {words} spoken words (aim for {words}-{max_words}). Conversational, vivid, concrete. No filler.
- {ending}
- Every sentence must be directly supported by the SOURCE. Do not add general conclusions, predictions or claims
  about significance that the SOURCE does not state; end by restating what the SOURCE established.
- Do not mention "section" or "chapter". Do not say like/subscribe. No medical, financial or legal advice.

Return JSON: {{"narration": str, "claims": [str]}}  // claims: each factual claim you made, one per item

SOURCE ({source_title}):
{source_text}
"""

SECTIONS = 7
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
        previous=(f"The previous section ended with: \"{prev}\" Continue naturally from it.\n" if prev
                  else "This is the opening of the video.\n"),
        ending=("End with a satisfying payoff that answers the opening question." if i == n - 1
                else "End with a mini open-loop that makes the viewer want the next section."),
    )
    if avoid:
        prompt += ("\nThe fact-checker judged these claims UNSUPPORTED by the SOURCE. Do not state them or anything "
                   "like them:\n" + "\n".join(f"- {c}" for c in avoid))
    out = gen(prompt)
    if _words(out.get("narration", "")) < per * 0.8:  # one targeted retry for an undershoot
        out = gen(prompt + f"\nYour last draft had only {_words(out.get('narration', ''))} words. Write at least {per}.")
    return {"heading": sec["heading"], "key_points": sec.get("key_points", []),
            "visual_query": sec.get("visual_query", ""), "narration": out.get("narration", "").strip(),
            "claims": out.get("claims", [])}


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
