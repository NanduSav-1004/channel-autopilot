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

LONG_PROMPT = """You are the scriptwriter for a faceless YouTube channel about {niche}.
Write a script about: "{topic}". Style: {style}
Use ONLY facts supported by the SOURCE below; do not invent numbers, dates or quotes.
If the source does not support a claim, leave it out. Never give medical, financial or legal advice.

Requirements:
- Target {words} spoken words total. Conversational, concrete, no filler, no clickbait lies.
- Open with a hook in the first 2 sentences that creates a real question the video answers.
- Re-hook every section with a mini open-loop. Finish with a satisfying payoff, not "like and subscribe".
- Each section needs a short visual_query (2-4 words) for stock footage/image search.

Return JSON: {{"title": str (<=70 chars), "description": str, "tags": [str],
"sections": [{{"heading": str, "narration": str, "visual_query": str}}],
"claims": [str]  // every factual claim made, one per item, for fact-checking
}}

SOURCE ({source_title}):
{source_text}
"""


def generate_script(
    topic: str, source: dict, niche: str, series: str | None = None, words: int = 1300,
    gen: Callable[[str], dict] = llm.generate_json,
) -> dict:
    series = series or random.choice(list(SERIES))
    prompt = LONG_PROMPT.format(
        niche=niche, topic=topic, style=SERIES[series], words=words,
        source_title=source["title"], source_text=source["text"],
    )
    script = gen(prompt)
    script["series"] = series
    script["source_url"] = source["url"]
    return script
