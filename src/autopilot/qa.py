"""QA gate: deterministic checks first (cheap), then an LLM fact-check against the source."""
import re
from collections.abc import Callable

from autopilot import llm

FACTCHECK_PROMPT = """You are a fact-checker. Using ONLY the SOURCE text, check each CLAIM.
Flag a claim as unsupported ONLY if it asserts something specific that the SOURCE does not state or clearly
imply, or that contradicts it: a number, date, name, place, quantity, cause, mechanism, ranking, or comparison.
Do NOT flag: rhetorical questions, hooks, transitions, sentences that only introduce or frame a topic, a common
misconception mentioned for contrast, or a paraphrase or reasonable summary of facts the SOURCE supports.
Return JSON: {{"unsupported": [str], "advice_given": bool, "notes": str}}
advice_given is true if the script gives medical, financial or legal advice.

SOURCE:
{source}

CLAIMS:
{claims}
"""


def deterministic_checks(
    script: dict, forbidden: list[str], min_words: int = 600, min_sections: int = 1
) -> list[str]:
    issues = []
    sections = script.get("sections") or []
    if not script.get("title") or len(script["title"]) > 100:
        issues.append("missing or too-long title")
    if not sections:
        issues.append("no sections")
    elif len(sections) < min_sections:
        issues.append(f"too few sections: {len(sections)} < {min_sections}")
    text = " ".join(s.get("narration", "") for s in sections).lower()
    if len(text.split()) < min_words:
        issues.append(f"too short: {len(text.split())} words < {min_words}")
    for term in forbidden:
        if term.lower() in text:
            issues.append(f"forbidden topic mentioned: {term}")
    if any(not s.get("visual_query") for s in sections):
        issues.append("section missing visual_query")
    return issues


def metadata_claims(script: dict) -> list[str]:
    """The title and each description sentence, tagged so a failure is routed to a metadata rewrite."""
    claims = []
    if script.get("title"):
        claims.append(f"[title] {script['title']}")
    for sentence in re.split(r"(?<=[.!?])\s+", script.get("description", "").strip()):
        if len(sentence.split()) >= 4:
            claims.append(f"[description] {sentence}")
    return claims


def check_script(
    script: dict, source: dict, forbidden: list[str],
    gen: Callable[[str], dict] = llm.generate_json, min_words: int = 600, min_sections: int = 1,
) -> list[str]:
    """Return a list of issues; empty means the script passes."""
    issues = deterministic_checks(script, forbidden, min_words, min_sections)
    if issues:
        return issues
    claims = "\n".join(f"- {c}" for c in script.get("claims", []) + metadata_claims(script))
    verdict = gen(FACTCHECK_PROMPT.format(source=source["text"], claims=claims))
    issues += [f"unsupported claim: {c}" for c in verdict.get("unsupported", [])]
    if verdict.get("advice_given"):
        issues.append("script gives medical/financial/legal advice")
    return issues


def _tokens(text: str) -> set[str]:
    return {w for w in "".join(c.lower() if c.isalnum() else " " for c in text).split() if len(w) > 3}


def locate_sections(script: dict, unsupported: list[str]) -> list[int]:
    """Which sections made these claims? Matches by word overlap, since the fact-checker may paraphrase."""
    found: set[int] = set()
    for claim in unsupported:
        ct = _tokens(claim)
        best, best_score = None, 0.0
        for i, sec in enumerate(script.get("sections", [])):
            for c in sec.get("claims", []) + [sec.get("narration", "")]:
                st = _tokens(c)
                score = len(ct & st) / (len(ct) or 1)
                if score > best_score:
                    best, best_score = i, score
        if best is not None and best_score >= 0.5:
            found.add(best)
    return sorted(found)
