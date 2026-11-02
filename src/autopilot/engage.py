"""Comment questions (approved 2026-11-02): every long video ends with ONE question the viewer can answer in a few words, spoken at the end
and shown as text; the same question is posted as the channel's own first comment once the video is public (see comments.py).

Four kinds rotate so the Saturday report can compare them: a pick-one/prediction, a personal one (the viewer's own place or experience), a
challenge/correct-us one, and a topic request. The question contains no facts and no numbers (so the fact-check has nothing to check) and
never promises a specific next video. No bait: nothing is offered for commenting."""
import re

from autopilot import llm

KINDS = ["pick", "personal", "correct", "request"]
KIND_TEXT = {
    "pick": "a pick-one or prediction question the viewer can answer with a word or two (which one, A or B, higher or lower, would you have guessed it)",
    "personal": "a question about the viewer's OWN experience or place (where they have noticed this, what they do about it, how it looks where they live)",
    "correct": "an invitation to challenge or extend the explanation (what would you question, what did we leave out, did this match what you were taught)",
    "request": "a question asking which topic the viewer would like explained next, answerable in a few words",
}
FALLBACK = {
    "pick": "Which part did you find hardest to believe?",
    "personal": "Where have you noticed this in your own life?",
    "correct": "What would you question in this explanation?",
    "request": "Which topic should we explain next?",
}
FALLBACK_DATA = {
    "pick": "Which of these numbers surprised you most?",
    "personal": "How does this look where you live?",
    "correct": "What do you think the data is missing?",
    "request": "Which number should we chart next?",
}
SUBSCRIBE = ["Subscribe if you want tomorrow's.", "A new one comes every day, so subscribe.", "Subscribe for the next one."]
BANNED = ("like and subscribe", "smash", "hit the", "bell", "in this video", "giveaway", "win ", "free ", "journey", "amazing", "fascinating",
          "comment yes", "comment below to", "dm me", "link in")
PROMPT = """Write ONE comment question for the end of a YouTube {genre} titled "{title}". The last thing the narrator said was: "{last}"

The question must be {kind}.
Rules: ONE question, 6 to 16 words, plain and friendly, no exclamation marks, no numbers or digits, no facts or claims, no hype words, nothing offered
in return, and never name or promise the next video. It must make sense to someone who just watched, and be easy to answer in one line.
Also give: "onscreen" (the same question cut to at most 7 words, no question needed to be complete, plain words) and "comment" (the question as a
friendly first comment from the channel, one or two short sentences, no emojis, no links).
Return JSON {{"question": str, "onscreen": str, "comment": str}}"""


def pick_kind(seed: int) -> str:
    return KINDS[seed % len(KINDS)]


def valid(q: str, max_words: int = 18) -> bool:
    low = q.lower()
    words = q.split()
    return (q.strip().endswith("?") and 4 <= len(words) <= max_words and q.count("?") == 1 and "!" not in q
            and not re.search(r"\d", q) and not any(b in low for b in BANNED))


def make_question(title: str, last: str, seed: int, gen=llm.generate_json, data: bool = False) -> dict:
    """{"kind", "question", "onscreen", "comment"}: from the model if it gives a clean one, else a plain fixed question of that kind."""
    kind = pick_kind(seed)
    fallback = (FALLBACK_DATA if data else FALLBACK)[kind]
    out = {"kind": kind, "question": fallback, "onscreen": fallback.rstrip("?").upper(), "comment": fallback}
    try:
        got = gen(PROMPT.format(title=title, last=last[-300:], kind=KIND_TEXT[kind], genre="data story" if data else "science explainer"))
        q = str(got.get("question", "")).strip()
        if valid(q):
            on = str(got.get("onscreen", "")).strip().rstrip("?")
            comment = str(got.get("comment", "")).strip()
            out |= {"question": q, "onscreen": (on if 2 <= len(on.split()) <= 8 and not re.search(r"\d", on) else q.rstrip("?")).upper(),
                    "comment": comment if q.lower().rstrip("?") in comment.lower() and len(comment) <= 300 and "http" not in comment else q}
    except (llm.LLMError, ValueError, AttributeError, TypeError):
        pass
    return out


def closing_line(engage: dict, seed: int) -> str:
    """The spoken ending: the question, a plain invitation to answer, and a very short subscribe clause."""
    return f"{engage['question']} Tell us in the comments. {SUBSCRIBE[seed % len(SUBSCRIBE)]}"


def extract_question(narration: str) -> str | None:
    """The last clean question in a narration (used for Plotline, whose writer includes it in the final act)."""
    qs = [s.strip() for s in re.findall(r"[^.?!]*\?", narration)]
    qs = [q for q in qs if valid(q, 22)]
    return qs[-1] if qs else None


def last_question(text: str, max_words: int = 30) -> str | None:
    """The last question in a narration in ANY language (used for the Malayalam edition, where the English word checks do not apply)."""
    qs = [q.strip() for q in re.findall(r"[^.?!\n]*\?", text) if 3 <= len(q.split()) <= max_words]
    return qs[-1] if qs else None
