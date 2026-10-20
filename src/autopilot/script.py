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
- Do not mention "section" or "chapter". Do not say like/subscribe. No medical, financial or legal advice.

Return JSON: {{"narration": str, "claims": [str]}}  // claims: each factual claim you made, one per item

SOURCE ({source_title}):
{source_text}
"""

SECTIONS = 7


def _words(text: str) -> int:
    return len(text.split())


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
    planned = script["sections"]
    per = round(words / len(planned))
    headings = " | ".join(s["heading"] for s in planned)
    done, claims, prev = [], list(script.get("claims", [])), ""
    for i, sec in enumerate(planned):
        last = i == len(planned) - 1
        prompt = SECTION_PROMPT.format(
            title=script["title"], style=style, headings=headings, num=i + 1, n=len(planned),
            heading=sec["heading"], points="; ".join(sec.get("key_points", [])), words=per,
            max_words=round(per * 1.3), source_title=source["title"], source_text=source["text"],
            previous=f"The previous section ended with: \"{prev}\" Continue naturally from it.\n" if prev else "This is the opening of the video.\n",
            ending="End with a satisfying payoff that answers the opening question." if last
            else "End with a mini open-loop that makes the viewer want the next section.",
        )
        out = gen(prompt)
        if _words(out.get("narration", "")) < per * 0.8:  # one targeted retry for an undershoot
            out = gen(prompt + f"\nYour last draft had only {_words(out.get('narration', ''))} words. Write at least {per}.")
        narration = out.get("narration", "").strip()
        done.append({"heading": sec["heading"], "narration": narration, "visual_query": sec.get("visual_query", "")})
        claims += out.get("claims", [])
        prev = " ".join(narration.split()[-30:])
    script.update({"sections": done, "claims": claims, "series": series, "source_url": source["url"]})
    return script
