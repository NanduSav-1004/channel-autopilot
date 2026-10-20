"""QA gate: deterministic checks first (cheap), then an LLM fact-check against the source."""
from collections.abc import Callable

from autopilot import llm

FACTCHECK_PROMPT = """You are a strict fact-checker. Using ONLY the SOURCE text, check each CLAIM.
Mark a claim unsupported if the source does not state or clearly imply it.
Return JSON: {{"unsupported": [str], "advice_given": bool, "notes": str}}
advice_given is true if the script gives medical, financial or legal advice.

SOURCE:
{source}

CLAIMS:
{claims}
"""


def deterministic_checks(script: dict, forbidden: list[str], min_words: int = 600) -> list[str]:
    issues = []
    sections = script.get("sections") or []
    if not script.get("title") or len(script["title"]) > 100:
        issues.append("missing or too-long title")
    if not sections:
        issues.append("no sections")
    text = " ".join(s.get("narration", "") for s in sections).lower()
    if len(text.split()) < min_words:
        issues.append(f"too short: {len(text.split())} words < {min_words}")
    for term in forbidden:
        if term.lower() in text:
            issues.append(f"forbidden topic mentioned: {term}")
    if any(not s.get("visual_query") for s in sections):
        issues.append("section missing visual_query")
    return issues


def check_script(
    script: dict, source: dict, forbidden: list[str],
    gen: Callable[[str], dict] = llm.generate_json, min_words: int = 600,
) -> list[str]:
    """Return a list of issues; empty means the script passes."""
    issues = deterministic_checks(script, forbidden, min_words)
    if issues:
        return issues
    claims = "\n".join(f"- {c}" for c in script.get("claims", []))
    verdict = gen(FACTCHECK_PROMPT.format(source=source["text"], claims=claims))
    issues += [f"unsupported claim: {c}" for c in verdict.get("unsupported", [])]
    if verdict.get("advice_given"):
        issues.append("script gives medical/financial/legal advice")
    return issues
