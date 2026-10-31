"""The closing line of a long video and the on-screen "full video" tag of a Short (call-to-action, approved 2026-10-31).

A long video ends with ONE short, spoken line that ties back to what the viewer just learned and invites them to subscribe for the next
explainer. The wording is written fresh for every video (the style rotates, so no two neighbours sound the same). It contains no facts
and no numbers, so the fact-check has nothing to check. A Short gets no spoken ask; for its last couple of seconds a tag on screen says the full
video is on the channel."""
import re

from autopilot import llm

STYLES = [
    "a curious question that points at tomorrow's explainer",
    "a warm invitation tied to what the viewer has just learned",
    "a promise that a new explainer lands every day",
    "a quick thank-you for watching, then the invitation",
    "a playful challenge: what should we take apart next?",
]
FALLBACKS = [
    "If this made you curious, subscribe: a new science explainer lands every day.",
    "Want to know how the next thing works? Subscribe, and we'll take it apart together.",
    "Thanks for watching. Subscribe, and tomorrow there's another explainer waiting for you.",
    "There's a lot more where this came from. Subscribe for a new science explainer every day.",
    "Curious what we'll uncover next? Subscribe and find out tomorrow.",
]
BANNED = ("like and subscribe", "smash", "hit the bell", "in this video", "comment below")
PROMPT = """Write the closing line of a YouTube science explainer titled "{title}". The last thing the narrator said was: "{last}"

Write ONE or TWO short spoken sentences (12 to 26 words in all) in the style of: {style}.
It must invite the viewer to subscribe for the next explainer, tie back to the topic in plain words (no facts, no numbers, no claims),
sound like a friendly presenter, and not use the phrases "like and subscribe", "smash", "hit the bell" or "in this video".
Return JSON {{"closing": str}}"""
SHORT_TAG = {"en": "FULL VIDEO ON THE CHANNEL", "ml": "പൂർണ്ണ വീഡിയോ ചാനലിൽ"}


def valid(line: str) -> bool:
    words = line.split()
    low = line.lower()
    return 8 <= len(words) <= 32 and "subscribe" in low and not re.search(r"\d", line) and not any(b in low for b in BANNED)


def make_closing(title: str, last: str, seed: int, gen=llm.generate_json) -> str:
    style = STYLES[seed % len(STYLES)]
    try:
        line = str(gen(PROMPT.format(title=title, last=last[-300:], style=style)).get("closing", "")).strip()
        if valid(line):
            return line
    except (llm.LLMError, ValueError, AttributeError):
        pass
    return FALLBACKS[seed % len(FALLBACKS)]


def add_closing(script: dict, seed: int, gen=llm.generate_json) -> dict:
    """Append the closing line to the last section's narration, once (the script remembers it)."""
    if script.get("closing") or not script.get("sections"):
        return script
    last = script["sections"][-1]
    line = make_closing(script.get("title", ""), last["narration"], seed, gen)
    last["narration"] = last["narration"].rstrip() + " " + line
    script["closing"] = line
    return script
