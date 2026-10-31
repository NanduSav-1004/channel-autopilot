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


COMPARISON_RE = re.compile(
    r"\bthan\b|\b(?:times|twice|double|triple|half|quarter|percent of|per cent of)\b|\b(?:float|floats|sink|sinks)\b|"
    r"\bas (?:much|many|big|large|heavy|dense|fast|old|long|hot|cold|bright|wide|tall) as\b|\b(?:lighter|heavier|denser|bigger|larger|smaller|faster|slower|"
    r"hotter|colder|brighter|older|younger|longer|shorter|wider|taller)\b", re.IGNORECASE)

COMPARE_PROMPT = """You check the COMPARISONS and MULTIPLES in a science script. For each numbered sentence, decide whether what it says about
size, weight, density, speed, age, temperature, how many times, half, double and so on is WRONG.
Use the SOURCE and well-known reference values (for example: water's density is 1 g/cm3 and Earth's is 5.51 g/cm3; anything denser than 1 g/cm3
sinks in water and is NOT lighter than water). CALCULATE: compare the numbers the sentence uses, and any numbers it implies, with the SOURCE.
Flag a sentence ONLY when its comparison or multiple is actually wrong or contradicts the SOURCE, not when it is merely unsourced or loosely phrased.
Return JSON {{"wrong": [{{"n": int, "why": str}}]}} (an empty list when all are right).

SOURCE:
{source}

SENTENCES:
{sentences}
"""


def comparison_sentences(script: dict) -> list[str]:
    """The sentences of the narration that make a comparison, a multiple or a sink-or-float claim (where models slip: "lighter than water")."""
    out = []
    for sec in script.get("sections") or []:
        out += [s for s in re.split(r"(?<=[.!?])\s+", sec.get("narration", "").strip()) if s and COMPARISON_RE.search(s)]
    return out


def comparison_issues(script: dict, source: dict, gen: Callable[[str], dict] = llm.generate_json) -> list[str]:
    """An independent check that reads the NARRATION itself, not the claims the writer chose to list: the writer's list once left out
    "it's lighter than water" about a density of 1.326 g/cm3. Returns the wrong sentences as unsupported claims (so they get repaired)."""
    sents = comparison_sentences(script)
    if not sents:
        return []
    prompt = COMPARE_PROMPT.format(source=source["text"], sentences="\n".join(f"{i + 1}. {s}" for i, s in enumerate(sents[:60])))
    out = {}
    for attempt in range(2):           # a busy model once made this check return nothing, silently: try again, and say so if it never answers
        try:
            out = gen(prompt)
            break
        except (llm.LLMError, KeyError, TypeError, ValueError, AttributeError) as exc:
            if attempt == 1:
                print(f"[qa] comparison check unavailable ({type(exc).__name__}); the other checks still apply", flush=True)
                return []              # a reviewer outage must not stop the daily video
    wrong = []
    for w in out.get("wrong", []) if isinstance(out, dict) else []:
        try:
            wrong.append(sents[int(w["n"]) - 1])
        except (KeyError, TypeError, ValueError, IndexError):
            continue
    return [f"unsupported claim: {s}" for s in dict.fromkeys(wrong)]


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
    issues += [i for i in comparison_issues(script, source, gen) if i not in issues]
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
