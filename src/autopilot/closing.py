"""The closing line of a long video and the on-screen "full video" tag of a Short (call-to-action, approved 2026-10-31).

A long video ends with ONE short, spoken line that ties back to what the viewer just learned and invites them to subscribe for the next
explainer. The wording is written fresh for every video (the style rotates, so no two neighbours sound the same). It contains no facts
and no numbers, so the fact-check has nothing to check. A Short gets no spoken ask; for its last couple of seconds a tag on screen says the full
video is on the channel."""
import re

from autopilot import llm

STYLES = [
    "a plain, curious question about what is worth understanding next",
    "a calm, one-sentence invitation tied to what was just explained",
    "a quiet promise that another explainer comes tomorrow",
    "a short thank-you, then the invitation",
]
FALLBACKS = [
    "If you want to understand the next one too, subscribe. There's a new explainer every day.",
    "That's the idea. Subscribe, and tomorrow there's another one to understand.",
    "Thanks for watching. A new science explainer comes out every day, so subscribe if you'd like the next.",
    "If this made you curious, subscribe. We'll take another one apart tomorrow.",
]
BANNED = ("like and subscribe", "smash", "hit the", "button", "bell", "in this video", "comment below", "journey", "wonders", "fascinating",
          "amazing", "join us", "join the", "together", "stay curious", "explore more", "hit subscribe", "tell me")
PROMPT = """Write the closing line of a YouTube science explainer titled "{title}". The last thing the narrator said was: "{last}"

Write ONE or TWO short spoken sentences, 12 to 22 words in all, in the style of: {style}. Do not repeat or quote the narrator's last words: start fresh. Never name or promise the next video's topic (it is not chosen yet); say only that a new explainer comes.
Tone: understated and plain, like a thoughtful teacher, not a presenter selling something. No exclamation marks, no hype words (amazing, journey,
wonders, fascinating), no "hit the button" or "join us", no "tell me". It must invite the viewer to subscribe for the next explainer and tie back
to the topic in plain words, with no facts, no numbers and no claims.
Examples of the tone (do not copy them): "That's how it works. If you'd like to understand the next one, subscribe. There's a new explainer every day."
and "Now you know why it behaves that way. Subscribe if you want to see what we take apart tomorrow."
Return JSON {{"closing": str}}"""
SHORT_TAG = {"en": "FULL VIDEO ON THE CHANNEL", "ml": "പൂർണ്ണ വീഡിയോ ചാനലിൽ"}


def valid(line: str) -> bool:
    words = line.split()
    low = line.lower()
    return 8 <= len(words) <= 26 and "subscribe" in low and "!" not in line and not re.search(r"\d", line) and not any(b in low for b in BANNED)


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
