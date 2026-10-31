"""Malayalam edition of a finished English video: translated script, Malayalam voice and captions, the same media.

Everything here uses its OWN Gemini key (GEMINI_API_KEY_ML, a separate free-tier project) so the English channel's
daily quota is never touched. Translation uses Gemini only: the Groq models produced garbled Malayalam."""
import contextlib
import itertools
import json
import os
import re
import wave
from collections.abc import Callable
from contextlib import contextmanager
from pathlib import Path

import numpy as np

from autopilot import closing, llm, tts
from autopilot.config import cta_on, mascot_style
from autopilot.shots import estimate_timings as shots_estimate_timings

TRANSLATE_MODELS = "gemini-3.5-flash,gemini-3.1-flash-lite,gemini-3.5-flash-lite"   # the last one is a fallback: both others were unavailable at once on 31 Oct
ML_VOICES = [{"engine": "gemini", "name": n} for n in ("Charon", "Achird", "Sulafat")]
FONT_ML_BOLD = "/usr/share/fonts/truetype/noto/NotoSansMalayalam-Bold.ttf"
ML_CAPTIONS = {"res": (1280, 720), "font": 46, "margin_v": 50, "group": 6, "upper": False, "outline": 5,
               "fontname": "Noto Sans Malayalam", "font_path": FONT_ML_BOLD}

QUOTES = str.maketrans("", "", "'\"‘’“”")
SENT_RE = re.compile(r"(?<=[.!?])\s+")


def split_sentences_ml(text: str) -> list[str]:
    """Malayalam has no capital letters, so a sentence ends at . ! ? followed by space."""
    return [s.strip() for s in SENT_RE.split(text.strip()) if s.strip()]


@contextmanager
def ml_quota():
    """Run LLM calls on the Malayalam project's Gemini key and Gemini models only."""
    key = os.environ.get("GEMINI_API_KEY_ML")
    if not key:
        raise OSError("GEMINI_API_KEY_ML is not set")
    saved = {k: os.environ.get(k) for k in ("GEMINI_API_KEY", "GEMINI_MODELS", "GROQ_API_KEY")}
    os.environ["GEMINI_API_KEY"], os.environ["GEMINI_MODELS"] = key, TRANSLATE_MODELS
    os.environ.pop("GROQ_API_KEY", None)
    try:
        yield
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


SECTION_PROMPT = """Translate this narration for a YouTube science explainer into natural SPOKEN Malayalam for a Kerala audience, in Malayalam script.
Rules: conversational and clear like a good presenter, not literal word-for-word and not stiff textbook language; short sentences
(each ends with . ? or !); keep common English technical terms (for example Mpemba effect, freezer, thermodynamics) the way Malayalam
speakers say them; keep every number, date and name accurate; add nothing that is not in the English and leave nothing out.
Return JSON {{"heading": str, "narration": str}}.

Heading: {heading}
Narration: {narration}"""

REPAIR_PROMPT = """

A reviewer found these problems in an earlier Malayalam translation of this text. Translate it again and fix every one of them:
{issues}
Earlier translation: {previous}"""

SEVERITY = """Classify every problem you list:
- "major": a number, date, name or unit that differs from the English; a claim that is in the Malayalam but NOT in the English;
  a meaning that is reversed or contradicted; a concrete fact stated wrongly.
- "minor": anything else: wording, nuance, simplification or generalisation, a metaphor made literal or the reverse, a part left
  out, reordering. Minor problems are acceptable: list them as "minor" (or leave them out)."""

CHECK_PROMPT = """You check a Malayalam translation of a science explainer's narration against the English original.
Look for substantive problems: a number, date, name, unit or fact that differs; something added that is not in the English; a
meaning that is reversed or distorted; an important sentence of the English that is missing.
""" + SEVERITY + """
Return JSON {{"issues": [{{"severity": "major" or "minor", "issue": str}}]}} (an empty list when the translation is faithful).
Describe each issue in English.

ENGLISH:
{english}

MALAYALAM:
{malayalam}"""

VERIFY_PROMPT = """A reviewer compared a Malayalam translation with its English original and reported the problems below.
Reviewers sometimes make mistakes or misread the meaning. For each reported problem, read the Malayalam carefully and
decide whether it is a REAL substantive error (the Malayalam really says something different from the English) or a
false alarm (the Malayalam matches the English, or the difference is only style).
Return JSON {{"real": [true or false for each problem, in order]}}.

ENGLISH:
{english}

MALAYALAM:
{malayalam}

REPORTED PROBLEMS:
{issues}"""

SHORT_PROMPT = """Translate this YouTube Short script (a science explainer, spoken in under {seconds} seconds) into natural SPOKEN Malayalam
for a Kerala audience, in Malayalam script.
Rules: conversational and punchy, short sentences (each ends with . ? or !); keep common English technical terms the way Malayalam
speakers say them; keep every number, date and name accurate and add nothing that is not in the English. Malayalam words are long,
so the WHOLE narration must be at most {max_words} Malayalam words: keep the hook first and the payoff last, and if it does not
fit, leave out the least important detail (never change a fact or a number).
Title: at most 60 characters, curiosity-driven and honest, Malayalam script (English terms may stay in English).
Return JSON {{"title": str, "narration": str}}.

Title: {title}
Narration: {narration}"""

SHORT_CHECK_PROMPT = """You check a Malayalam Short script against its English original. The Malayalam is deliberately shorter: it may leave out
details and simplify. It must not CHANGE or ADD facts.
""" + SEVERITY + """
Return JSON {{"issues": [{{"severity": "major" or "minor", "issue": str}}]}} (an empty list when faithful). Describe each in English.

ENGLISH:
{english}

MALAYALAM:
{malayalam}"""

OMIT_PROMPT = """

The earlier translations still had these problems:
{issues}
Earlier translation: {previous}
Translate once more, and this time LEAVE OUT every sentence or detail that you cannot translate exactly as the English says it. A
shorter script with only exact statements is fine. Keep the hook first and a payoff sentence last."""

SENTENCE_PROMPT = """Translate this ONE sentence from a science Short into natural SPOKEN Malayalam, in Malayalam script. Keep numbers, names and
meaning exactly; keep common English technical terms as Malayalam speakers say them; add nothing.
Return JSON {{"text": str}}.

Sentence: {sentence}"""

META_PROMPT = """Translate this YouTube video's metadata into Malayalam for a Kerala audience.
- title: natural and curiosity-driven, at most 70 characters, keep the main keyword (English terms may stay in English).
- thumbnail_text: 2-4 punchy words for the thumbnail, Malayalam script.
- description: 2-3 sentences, then a new paragraph exactly: "ഈ വീഡിയോയുടെ തിരക്കഥ AI സഹായത്തോടെ തയ്യാറാക്കിയതും ശബ്ദം കൃത്രിമവുമാണ്."
- tags: 10-15 tags mixing Malayalam and English search terms.
Return JSON {{"title": str, "thumbnail_text": str, "description": str, "tags": [str]}}.

Title: {title}
Thumbnail text: {thumb}
Description: {description}"""


NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")
THOUSANDS_RE = re.compile(r"(?<=\d)[,\u202f\u00a0\u2009 ](?=\d{3}(?!\d))")


def numbers_in(text: str) -> list[str]:
    """The numbers a text contains, with thousands separators removed: "3\u202f000", "3,000" and "3000" are the same number.
    (English scripts use narrow no-break spaces between digit groups, which once made "3 000 km" look like two numbers.)"""
    return NUMBER_RE.findall(THOUSANDS_RE.sub("", text))
REPAIR_ROUNDS = 2


class TranslationRejected(RuntimeError):
    """The Malayalam still disagrees with the English after repairs: the edition is not published."""


def missing_numbers(english: str, malayalam: str) -> list[str]:
    """Numbers written in the English that do not appear in the Malayalam (digits must be kept as digits)."""
    have = set(numbers_in(malayalam))
    return sorted({n for n in numbers_in(english) if n not in have})


def major_issues(reported) -> list[str]:
    """Only the problems a reviewer calls major count; a bare string (an older style answer) is treated as major."""
    out = []
    for r in reported or []:
        if isinstance(r, dict):
            if str(r.get("severity", "major")).lower() == "major":
                out.append(str(r.get("issue", r)))
        else:
            out.append(str(r))
    return out


def check_translation(english: str, malayalam: str, gen: Callable[[str], dict]) -> list[str]:
    """Problems found, in English: numbers that went missing (exact check) plus what the model reviewer reports."""
    issues = [f"the number {n} from the English is missing" for n in missing_numbers(english, malayalam)]
    try:
        reported = major_issues(gen(CHECK_PROMPT.format(english=english, malayalam=malayalam)).get("issues", []))
        if reported:     # a second look filters the reviewer's own false alarms
            real = gen(VERIFY_PROMPT.format(english=english, malayalam=malayalam,
                                            issues="\n".join(f"{i + 1}. {r}" for i, r in enumerate(reported)))).get("real", [])
            if len(real) != len(reported):
                real = [True] * len(reported)
            issues += [r for r, ok in zip(reported, real, strict=True) if ok is True]
    except (llm.LLMError, KeyError, TypeError, ValueError, AttributeError):
        pass     # the exact checks above still applied; a reviewer outage must not block the edition
    return issues


def added_numbers(english: str, malayalam: str) -> list[str]:
    """Numbers in the Malayalam that the English does not have (a Short may leave details out, never invent a number)."""
    have = set(numbers_in(english))
    return sorted({n for n in numbers_in(malayalam) if n not in have})


def check_short(english: str, malayalam: str, gen: Callable[[str], dict]) -> list[str]:
    issues = [f"the number {n} is not in the English" for n in added_numbers(english, malayalam)]
    try:
        reported = major_issues(gen(SHORT_CHECK_PROMPT.format(english=english, malayalam=malayalam)).get("issues", []))
        if reported:
            real = gen(VERIFY_PROMPT.format(english=english, malayalam=malayalam,
                                            issues="\n".join(f"{i + 1}. {r}" for i, r in enumerate(reported)))).get("real", [])
            if len(real) != len(reported):
                real = [True] * len(reported)
            issues += [r for r, ok in zip(reported, real, strict=True) if ok is True]
    except (llm.LLMError, KeyError, TypeError, ValueError, AttributeError):
        pass
    return issues


def translate_short(short: dict, max_words: int, gen: Callable[[str], dict] = llm.generate_json,
                    log: Callable[[str], None] = print) -> dict:
    """A Short's Malayalam title and narration: translated to fit `max_words`, checked, repaired, or rejected."""
    prompt = SHORT_PROMPT.format(seconds=52, max_words=max_words, title=short["title"], narration=short["narration"])
    out = gen(prompt)
    for attempt in range(REPAIR_ROUNDS + 2):
        narration, title = str(out["narration"]).strip(), str(out.get("title", short["title"])).strip()
        issues = check_short(short["narration"], narration, gen) if narration else ["the translation is empty"]
        if len(narration.split()) > max_words * 1.15:
            issues.append(f"too long: {len(narration.split())} words, the limit is {max_words}")
        if not issues:
            return {"title": title[:70], "narration": narration}
        if attempt == REPAIR_ROUNDS + 1:
            log(f"[ml] the Short {short['title']!r} still has problems ({'; '.join(issues[:2])}); translating it sentence by sentence")
            return translate_short_by_sentence(short, max_words, gen, log)
        log(f"[ml] repairing the Short {short['title']!r}: {'; '.join(issues[:2])}")
        text = "\n".join(f"- {i}" for i in issues)
        extra = OMIT_PROMPT if attempt == REPAIR_ROUNDS else REPAIR_PROMPT         # the last round may leave a detail out
        out = gen(prompt + extra.format(issues=text, previous=narration))
    raise AssertionError("unreachable")


def translate_short_by_sentence(short: dict, max_words: int, gen: Callable[[str], dict] = llm.generate_json,
                                log: Callable[[str], None] = print) -> dict:
    """The last resort that keeps "a Malayalam Short for every English Short" a rule: translate and check ONE sentence at a time (each is
    small and easy to get exactly right) and leave out any sentence that cannot be made faithful in two tries. The Short is shorter but
    never wrong. Raises TranslationRejected if fewer than four sentences survive."""
    english = [s for s in re.split(r"(?<=[.!?])\s+", short["narration"].strip()) if s]
    kept: list[str] = []
    for sent in english:
        for _ in range(2):
            try:
                text = str(gen(SENTENCE_PROMPT.format(sentence=sent)).get("text", "")).strip()
            except (llm.LLMError, KeyError, TypeError, ValueError, AttributeError):
                continue
            if text and not check_short(sent, text, gen):
                kept.append(text)
                break
        else:
            log(f"[ml] left out one sentence of the Short {short['title']!r}: it could not be translated faithfully")
    while len(" ".join(kept).split()) > max_words * 1.15 and len(kept) > 4:
        kept.pop(len(kept) // 2)                    # too long: drop from the middle, keeping the hook and the payoff
    if len(kept) < 4:
        raise TranslationRejected(f"Short {short['title']!r}: only {len(kept)} sentence(s) could be translated faithfully")
    title = str(short["title"])
    try:
        title = str(gen(SENTENCE_PROMPT.format(sentence=short["title"])).get("text", "")).strip() or title
    except (llm.LLMError, KeyError, TypeError, ValueError, AttributeError):
        pass
    return {"title": title[:70], "narration": " ".join(kept)}


def translate_section(sec: dict, gen: Callable[[str], dict], log: Callable[[str], None] = print) -> dict:
    """One section, translated, checked against the English, and re-translated with the problems as feedback."""
    prompt = SECTION_PROMPT.format(heading=sec["heading"], narration=sec["narration"])
    out = gen(prompt)
    for attempt in range(REPAIR_ROUNDS + 1):
        narration = str(out["narration"]).strip()
        issues = check_translation(sec["narration"], narration, gen) if narration else ["the translation is empty"]
        if not issues:
            return {"heading": str(out.get("heading", sec["heading"])).strip(), "narration": narration}
        if attempt == REPAIR_ROUNDS:
            raise TranslationRejected(f"{sec['heading']!r}: " + "; ".join(issues[:3]))
        log(f"[ml] repairing the translation of {sec['heading']!r}: {'; '.join(issues[:2])}")
        out = gen(prompt + REPAIR_PROMPT.format(issues="\n".join(f"- {i}" for i in issues), previous=narration))
    raise AssertionError("unreachable")


def translate_script(script: dict, gen: Callable[[str], dict] = llm.generate_json) -> dict:
    """The Malayalam script: same sections, same order, translated and fact-checked against the English."""
    sections = [translate_section(sec, gen) for sec in script["sections"]]
    meta = gen(META_PROMPT.format(title=script["title"], thumb=script.get("thumbnail_text", ""),
                                  description=script.get("description", "")))
    from autopilot.script import shorten_title
    ml = {"title": str(meta["title"]).strip(), "thumbnail_text": str(meta["thumbnail_text"]).strip(),
          "description": str(meta["description"]).strip(), "tags": [str(t) for t in meta.get("tags", [])],
          "series": script.get("series", ""), "sections": sections, "source_url": script.get("source_url")}
    shorten_title(ml, gen=gen)
    return ml


# ---------- Malayalam voice: Gemini (no timing in its audio), sentences located from silences ----------
def _frame_rms(pcm: bytes, rate: int, win: float = 0.02) -> np.ndarray:
    a = np.frombuffer(pcm, dtype="<i2").astype(float)
    n = max(1, int(rate * win))
    a = a[: len(a) // n * n].reshape(-1, n)
    return np.sqrt((a ** 2).mean(axis=1))


VIRAMA = "്"
SPOKEN_DIGITS = {1: 2, 2: 6, 3: 9, 4: 13}      # syllables when a number is read out in Malayalam (1905 is about thirteen)


OPERATORS = {"=": 3.0, "+": 1.5, "−": 1.5, "×": 2.0, "÷": 2.0, "/": 1.5, "^": 1.5, "±": 2.0, "≈": 2.0, "≤": 2.0, "≥": 2.0,
             "<": 1.5, ">": 1.5, "²": 3.0, "³": 3.0, "√": 2.0, "∞": 2.5, "∑": 2.0, "∫": 2.0, "∂": 2.0, "°": 1.5}
UNIT_WORDS = {"tb/s": 9, "gb/s": 9, "mb/s": 9, "kb/s": 9, "km/h": 7, "m/s": 5, "m/s²": 8, "ghz": 5, "mhz": 5, "khz": 5, "thz": 5,
              "kw": 4, "mw": 4, "gw": 4, "tw": 4, "kv": 4, "ev": 3, "mev": 4, "gev": 4, "tev": 4, "°c": 4, "°f": 4}
LETTER_SYLLABLES = 1.2     # a Latin letter read as its name ("എം", "സി"); Greek letters ("ഡെൽറ്റ", "ന്യൂ") take two


def formula_weight(token: str) -> float | None:
    """The spoken length of an equation, unit or symbol-laden token such as "E=mc²", "ΔE", "H₂O" or "Tb/s", or None if the token is
    an ordinary word. Gemini reads these out letter by letter and symbol by symbol ("E equals m c squared"), so the
    captions that treated them as one short word flipped far ahead of the voice."""
    bare = token.strip("(),;:.!?\"'“”‘’")
    if re.search(r"[ക-ഹഅ-ഔ]", bare):                         # contains Malayalam: an ordinary word (like "CPU-നുള്ളിൽ")
        return None
    if bare.lower() in UNIT_WORDS:
        return float(UNIT_WORDS[bare.lower()])
    symbols = any(c in OPERATORS or c in "₀₁₂₃₄₅₆₇₈₉" for c in bare) or bool(re.search(r"[α-ωΑ-Ω]", bare))
    mixed = bool(re.search(r"[A-Za-z]", bare) and re.search(r"[0-9]", bare))
    if not (symbols or mixed):
        return None                                             # "Wi-Fi", "opcode", "CPU": ordinary words
    n = 0.0
    for m in re.finditer(r"\d+(?:[.,]\d+)?|[A-Za-z]|[α-ωΑ-Ω]|[₀-₉]|\S", bare):
        s = m.group()
        if re.fullmatch(r"[0-9]+(?:[.,][0-9]+)?", s):
            digits = len(re.sub(r"[^0-9]", "", s))
            n += SPOKEN_DIGITS.get(digits, 3 * digits)
        elif s in OPERATORS:
            n += OPERATORS[s]
        elif s.isascii() and s.isalpha():
            n += LETTER_SYLLABLES
        elif re.match(r"[α-ωΑ-Ω]", s):
            n += 2.0
        elif s in "₀₁₂₃₄₅₆₇₈₉":
            n += 1.0
        elif s == "-":
            n += 1.5
        else:
            n += 0.5
    return max(1.0, n)


def spoken_weight(token: str) -> float:
    """How long a word takes to SAY, in syllables: Malayalam by aksharas (a consonant with its vowel is one, a consonant
    closing a syllable or joining a conjunct is none), Latin words by vowel groups, and numbers by how they are read aloud.
    Letter counts badly under-weight numbers: "1905" is five letters but over a second of speech, and every caption word after
    it ran early until the next pause."""
    formula = formula_weight(token)
    if formula is not None:
        return formula
    n = 0.0
    rest = token
    for m in re.finditer(r"\d+(?:[.,]\d+)?", token):
        digits = len(re.sub(r"\D", "", m.group()))
        n += SPOKEN_DIGITS.get(digits, 3 * digits) + (2 if "." in m.group() else 0)
        rest = rest.replace(m.group(), "", 1)
    chars = list(rest)
    for i, c in enumerate(chars):
        if "അ" <= c <= "ഔ" or "ക" <= c <= "ഹ" and (chars[i + 1] if i + 1 < len(chars) else "") != VIRAMA:                                       # independent vowels
            n += 1
    lat = "".join(ch for ch in rest if ch.isascii() and ch.isalpha())
    if lat:
        n += len(lat) if lat.isupper() and len(lat) <= 5 else max(1, len(re.findall(r"[aeiouyAEIOUY]+", lat)))
    if re.search(r"\d", token) and re.search(r"[ക-ഹൺ-ൿ]", rest):   # "1905-ൽ": the suffix is one more syllable
        n += 1
    return max(1.0, n)


def _letters(sentence: str) -> float:
    """The spoken length of a text, in syllables (the name is historical: it used to count letters)."""
    return max(1.0, sum(spoken_weight(tok) for tok in sentence.split()))


def align_by_silence(sentences: list[str], pcm: bytes, rate: int) -> tuple[bytes, list[tuple[float, float]]]:
    """Trim leading/trailing silence and noise, and find each sentence's span: proportional to its letters, with each
    boundary moved to the nearest real pause. Returns (trimmed pcm, spans relative to it)."""
    win = 0.02
    rms = _frame_rms(pcm, rate, win)
    peak = float(np.percentile(rms, 98)) or 1.0
    loud = rms > 0.06 * peak
    idx = np.flatnonzero(loud)
    if not len(idx):
        raise OSError("the Malayalam narration is silent")
    first, last = int(idx[0]), int(idx[-1])
    start = max(0.0, first * win - 0.08)
    end = min(len(rms) * win, (last + 1) * win + 0.25)
    quiet = ~loud
    w = np.array([_letters(s) for s in sentences], dtype=float)
    cuts = np.cumsum(w)[:-1] / w.sum() * (end - start) + start
    bounds = []
    for c in cuts:
        lo, hi = int(max(first, (c - 0.7) / win)), int(min(last, (c + 0.7) / win))
        runs, i = [], lo
        while i <= hi:
            if quiet[i]:
                j = i
                while j + 1 <= hi and quiet[j + 1]:
                    j += 1
                if (j - i + 1) * win >= 0.12:        # a real pause, not a stop consonant
                    runs.append(((i + j + 1) / 2 * win, (j - i + 1) * win))
                i = j + 1
            else:
                i += 1
        bounds.append(min(runs, key=lambda r: abs(r[0] - c) - 0.3 * r[1])[0] if runs else float(c))
    edges = [start, *sorted(bounds), end]
    a, b = int(start * rate) * 2, int(end * rate) * 2
    return pcm[a:b], [(edges[i] - start, edges[i + 1] - start) for i in range(len(sentences))]


class MalayalamGeminiEngine(tts.GeminiEngine):
    """Gemini voice speaking Malayalam on the Malayalam project's key, with no English direction (Gemini reads
    such a direction aloud)."""
    key_env = "GEMINI_API_KEY_ML"
    style = ""
    estimate_words_only = True
    splitter = staticmethod(split_sentences_ml)

    def synth_section(self, sentences: list[str]):
        pcm = self._speak(" ".join(sentences).translate(QUOTES))   # quote marks make Gemini act the quote as a second voice
        pcm, cut = tts.trim_tail_artifact(pcm, 24000)
        if cut:
            print(f"[tts] cut {cut:.2f}s of noise from the end of a section", flush=True)
        pcm, spans = align_by_silence(sentences, pcm, 24000)
        pcm = tts.fade_out(pcm, 24000)
        return pcm, 24000, spans


def pick_ml_voice(video_number: int, voices: list[dict] | None = None) -> dict:
    """Rotating voice, never the same twice in a row (deterministic from the English job's number)."""
    return tts.pick_voice(video_number, voices or ML_VOICES)


def segment_by_pauses(weights: list[float], gaps: list[tuple[float, float]], t0: float, t1: float,
                      comma_slack: list[float] | None = None) -> list[tuple[float, float]]:
    """Cut [t0, t1] into len(weights) consecutive spans, one per piece of text, cutting only at real pauses where possible.
    The spans' lengths should be proportional to the weights (letters), and longer pauses are better cut points; a dynamic
    programme picks the best pauses, so one wrong pick cannot push every later piece out of place. When the audio has too
    few pauses, a cut at the proportional position stands in for the missing one."""
    n = len(weights)
    if n == 1:
        return [(t0, t1)]
    inner = [g for g in gaps if t0 < (g[0] + g[1]) / 2 < t1]
    speech = max(0.1, (t1 - t0) - sum(b - a for a, b in inner))
    pace = speech / max(1.0, sum(weights))
    cum = np.cumsum(weights)[:-1] / sum(weights)
    cands = [(a, b, -0.8 * min(b - a, 0.6)) for a, b in inner] + [(t0 + f * (t1 - t0),) * 2 + (0.7,) for f in cum]
    cands.sort(key=lambda c: (c[0], c[1]))
    slack = comma_slack or [0.0] * n
    exp = [w * pace + sl for w, sl in zip(weights, slack, strict=True)]

    def cost(i: int, start: float, stop: float) -> float:
        return 4.0 * ((stop - start - exp[i]) / max(exp[i], 0.5)) ** 2

    m = len(cands)
    best = [[float("inf")] * m for _ in range(n - 1)]
    back = [[-1] * m for _ in range(n - 1)]
    for j, c in enumerate(cands):
        best[0][j] = cost(0, t0, c[0]) + c[2]
    for i in range(1, n - 1):
        for j, c in enumerate(cands):
            for k in range(j):
                if best[i - 1][k] == float("inf") or cands[k][1] > c[0] + 1e-9:
                    continue
                v = best[i - 1][k] + cost(i, cands[k][1], c[0]) + c[2]
                if v < best[i][j]:
                    best[i][j], back[i][j] = v, k
    last, jbest = float("inf"), -1
    for j, c in enumerate(cands):
        if best[n - 2][j] < float("inf") and c[1] < t1:
            v = best[n - 2][j] + cost(n - 1, c[1], t1)
            if v < last:
                last, jbest = v, j
    if jbest < 0:   # no consistent choice: proportional spans
        edges = [t0] + [t0 + f * (t1 - t0) for f in cum] + [t1]
        return list(itertools.pairwise(edges))
    chosen = [jbest]
    for i in range(n - 2, 0, -1):
        chosen.append(back[i][chosen[-1]])
    chosen.reverse()
    spans, start = [], t0
    for j in chosen:
        spans.append((start, cands[j][0]))
        start = cands[j][1]
    spans.append((start, t1))
    return spans


def words_in(span: tuple[float, float], words: list[str]) -> list[dict]:
    """Words spread over a span in proportion to their letters."""
    w = np.array([_letters(x) for x in words], dtype=float)
    edges = span[0] + np.concatenate([[0.0], np.cumsum(w)]) / w.sum() * (span[1] - span[0])
    return [{"w": x, "s": round(float(a), 3), "e": round(float(b), 3)} for x, a, b in zip(words, edges[:-1], edges[1:], strict=True)]


def place_words(words: list[str], gaps: list[tuple[float, float]], t0: float, t1: float) -> list[dict]:
    """Time the words of one sentence spanning [t0, t1]. Pauses inside the sentence (a dramatic pause in a hook, a breath
    after a comma) are matched to word boundaries by a small dynamic programme: between two used pauses the words should
    take time proportional to their letters. A pause that fits no boundary well is treated as a hesitation and skipped."""
    n = len(words)
    inner = [g for g in gaps if g[1] - g[0] >= 0.15 and t0 + 0.12 < g[0] and g[1] < t1 - 0.12]
    if n == 1 or not inner:
        return words_in((t0, t1), words)
    wl = np.array([_letters(w) for w in words], dtype=float)
    cum = np.concatenate([[0.0], np.cumsum(wl)])
    pace = max(0.02, ((t1 - t0) - sum(b - a for a, b in inner)) / cum[-1])
    pts = [(t0, t0)] + inner                           # pts[0] is the sentence start; "used" pauses follow
    k = len(inner)
    best = {(0, 0): (0.0, None)}                       # (pause index, boundary after word index) -> (cost, previous state)

    def seg_cost(j0: int, b0: int, j1: int | None, b1: int) -> float:
        start = pts[j0][1]
        stop = t1 if j1 is None else pts[j1][0]
        skipped = sum(pts[m][1] - pts[m][0] for m in range(j0 + 1, (k + 1) if j1 is None else j1))
        expect = pace * (cum[b1] - cum[b0]) + skipped
        c = ((stop - start - expect) / max(expect, 0.4)) ** 2
        skip_pen = sum(0.3 + 1.5 * (pts[m][1] - pts[m][0]) for m in range(j0 + 1, (k + 1) if j1 is None else j1))   # a long pause is rarely a hesitation
        return c + skip_pen - (0.4 if b1 < n and words[b1 - 1][-1:] in ",;:" else 0.0)

    for j in range(1, k + 1):
        for b in range(1, n):
            cands = [(v[0] + seg_cost(j0, b0, j, b), (j0, b0)) for (j0, b0), v in best.items() if j0 < j and b0 < b]
            if cands:
                best[(j, b)] = min(cands, key=lambda c: c[0])
    final = [(v[0] + seg_cost(j0, b0, None, n), s) for s, v in best.items() for j0, b0 in [s]]
    _, state = min(final, key=lambda c: c[0])
    chain = []
    while state is not None:
        chain.append(state)
        state = best[state][1]
    chain.reverse()                                    # [(0, 0), (j1, b1), ...]
    out: list[dict] = []
    for idx, (j0, b0) in enumerate(chain):
        j1, b1 = chain[idx + 1] if idx + 1 < len(chain) else (None, n)
        span = (pts[j0][1], t1 if j1 is None else pts[j1][0])
        out += words_in(span, words[b0:b1])
    return out


def phrases(sentence: str) -> list[str]:
    """A sentence broken after each comma (the voice pauses there)."""
    parts = re.split(r"(?<=[,;:])\s+", sentence.strip())
    return [p for p in parts if p]


def ml_add_word_times(out_wav: Path, timings: list[dict], gaps: list[tuple[float, float]] | None = None) -> int:
    """Time every sentence, comma-phrase and word from the audio's own pauses (see segment_by_pauses). Returns how
    many sections were timed."""
    gaps = pauses(out_wav) if gaps is None else gaps
    with wave.open(str(out_wav)) as w:
        rate = w.getframerate()
        pcm = w.readframes(w.getnframes())
    rms = _frame_rms(pcm, rate)
    loud = np.flatnonzero(rms > 0.06 * (float(np.percentile(rms, 98)) or 1.0))
    for sec in timings:
        if not sec["sentences"]:
            continue
        a, b = int(sec["start"] / 0.02), int(sec["end"] / 0.02)
        idx = loud[(loud >= a) & (loud <= b)]
        if not len(idx):
            continue
        t0, t1 = float(idx[0]) * 0.02, float(idx[-1] + 1) * 0.02
        texts = [s["text"] for s in sec["sentences"]]
        spans = segment_by_pauses([_letters(x) for x in texts], gaps, t0, t1,
                                  [0.25 * (len(phrases(x)) - 1) for x in texts])
        for sent, (s0, s1) in zip(sec["sentences"], spans, strict=True):
            inside = [g for g in gaps if s0 < (g[0] + g[1]) / 2 < s1]
            sent["start"], sent["end"], sent["words"] = round(s0, 3), round(s1, 3), place_words(sent["text"].split(), inside, s0, s1)
    return sum(1 for sec in timings if sec["sentences"] and "words" in sec["sentences"][0])


def pauses(wav: Path, min_len: float = 0.12) -> list[tuple[float, float]]:
    """(start, end) of every real pause in the narration."""
    with wave.open(str(wav)) as w:
        rate = w.getframerate()
        pcm = w.readframes(w.getnframes())
    rms = _frame_rms(pcm, rate)
    quiet = rms < 0.06 * (float(np.percentile(rms, 98)) or 1.0)
    out, i, n = [], 0, len(quiet)
    while i < n:
        if quiet[i]:
            j = i
            while j + 1 < n and quiet[j + 1]:
                j += 1
            if (j - i + 1) * 0.02 >= min_len:
                out.append((i * 0.02, (j + 1) * 0.02))
            i = j + 1
        else:
            i += 1
    return out


def pace_outliers(timings: list[dict], tolerance: float = 0.45) -> int:
    """Sanity check on the timing: a sentence should take about as long as its letters suggest (compared with the whole
    video's pace). Counts sentences more than `tolerance` away; a high count would mean sentences were cut at wrong pauses."""
    rows = [(_letters(s["text"]), s["end"] - s["start"]) for sec in timings for s in sec["sentences"]]
    pace = sum(d for _, d in rows) / max(1, sum(n for n, _ in rows))
    return sum(1 for n, d in rows if abs(d - n * pace) > tolerance * n * pace + 0.5)


def make_monotone(timings: list[dict]) -> None:
    """Words and sentences must run forward in time, each word at least a few ms long, inside its sentence."""
    prev_end = 0.0
    for sec in timings:
        for sent in sec["sentences"]:
            ws = sent["words"]
            sent["start"] = max(sent["start"], prev_end - 0.0, sec["start"])
            t = sent["start"]
            for w in ws:
                w["s"] = round(max(w["s"], t), 3)
                w["e"] = round(max(w["e"], w["s"] + 0.03), 3)
                t = w["s"] + 0.02
            sent["end"] = round(max(sent["end"], ws[-1]["e"] if ws else sent["start"] + 0.05), 3)
            sent["start"] = round(sent["start"], 3)
            prev_end = sent["start"]


def pause_agreement(wav: Path, timings: list[dict], tol: float = 0.25) -> float:
    """Independent sync check: Gemini pauses between sentences, so each sentence start (after the first of a section)
    should sit at or next to a real pause in the audio. Returns the share that do."""
    with wave.open(str(wav)) as w:
        rate = w.getframerate()
        pcm = w.readframes(w.getnframes())
    rms = _frame_rms(pcm, rate)
    quiet = rms < 0.06 * (float(np.percentile(rms, 98)) or 1.0)
    hits = total = 0
    for sec in timings:
        for sent in sec["sentences"][1:]:
            k = int(sent["start"] / 0.02)
            span = int(tol / 0.02)
            total += 1
            hits += bool(quiet[max(0, k - span): k + span + 1].any())
    return hits / total if total else 1.0


def make_voice(script_ml: dict, out_wav: Path, voice: dict) -> list[dict]:
    timings = tts.synthesize_script(script_ml, out_wav, MalayalamGeminiEngine(voice["name"]), None)
    fixed = ml_add_word_times(out_wav, timings)
    make_monotone(timings)
    odd = pace_outliers(timings)
    print(f"[ml] timing: {fixed}/{len(timings)} sections cut at the audio's pauses; "
          f"{odd} sentence(s) of {sum(len(s['sentences']) for s in timings)} have an unusual pace", flush=True)
    return timings


def recover_media(src_dir: Path, timings: list[dict], topic: str, gather=None, use_nasa: bool = False) -> None:
    """The English run's media is gone (a later run, or a manual one): find new images and footage for the same script, on the
    Malayalam project's quota, and write items.json and credits.json so the edition can be built."""
    from autopilot import shots

    script = json.loads((src_dir / "script.json").read_text())
    plan = shots.plan_shots(timings)
    if gather is None:
        with ml_quota():
            items, credits = shots.gather_images(script, plan, Path("work") / "assets", topic, use_nasa=use_nasa)
    else:
        items, credits = gather(script, plan, topic)
    (src_dir / "items.json").write_text(json.dumps([[{"kind": i["kind"], "path": str(i["path"])} for i in sec] for sec in items]))
    (src_dir / "credits.json").write_text(json.dumps(credits))
    print(f"[ml] media rebuilt: {sum(len(s) for s in items)} items for {len(items)} sections", flush=True)


def build_edition(src_dir: Path, out_dir: Path, work: Path, voice: dict, translate=translate_script, topic: str = "",
                  mascot: str | None = None, use_nasa: bool = False) -> Path:
    """Make the Malayalam video from an English job directory (script.json, items.json, credits.json)."""
    from autopilot import audio, shots, thumbnail
    from autopilot.render import render_photo_video

    out_dir.mkdir(parents=True, exist_ok=True)
    script = json.loads((src_dir / "script.json").read_text())
    sp = out_dir / "script_ml.json"
    if sp.exists():
        ml = json.loads(sp.read_text())
    else:
        with ml_quota():
            ml = translate(script)
        sp.write_text(json.dumps(ml, ensure_ascii=False, indent=1))
    print(f"[ml] translated: {ml['title']!r}", flush=True)
    tp, wav = out_dir / "timings.json", out_dir / "narration.wav"
    if tp.exists() and wav.exists():
        timings = json.loads(tp.read_text())
    else:
        timings = make_voice(ml, wav, voice)
        tp.write_text(json.dumps(timings, ensure_ascii=False))
    print(f"[ml] voice {voice['name']}: {timings[-1]['end']:.0f}s", flush=True)
    if not (src_dir / "items.json").exists():
        recover_media(src_dir, timings, topic or script.get("title", ""), use_nasa=use_nasa)
    items = shots.fill_sparse_sections([[{"kind": i["kind"], "path": Path(i["path"])} for i in sec]
                                        for sec in json.loads((src_dir / "items.json").read_text())])
    music = audio.generate_ambient(timings[-1]["end"] + 5, out_dir / "music.wav", seed=1)
    final = out_dir / "final.mp4"
    en_total = json.loads((src_dir / "timings.json").read_text())[-1]["end"] if (src_dir / "timings.json").exists() else 0
    cut = shots.CUT_SECONDS * max(1.0, timings[-1]["end"] / en_total) if en_total else shots.CUT_SECONDS
    plan = shots.plan_cuts(timings, [len(s) for s in items], cut_seconds=cut)   # longer audio, same number of shots
    render_photo_video(ml, timings, items, plan, wav, final, work,
                       music=music, look=ML_CAPTIONS, mascot=mascot)
    images = [i["path"] for sec in items for i in sec if i["kind"] == "image"]
    thumbnail.make_thumbnail(ml, images, out_dir / "thumbnail.jpg", lang="ml")
    return final


# ---------- Malayalam Shorts ----------
ML_SHORT_CAPTIONS = {"res": (1080, 1920), "font": 78, "margin_v": 600, "group": 3, "upper": False, "outline": 10,
                     "fontname": "Noto Sans Malayalam", "font_path": FONT_ML_BOLD}
SHORT_MAX_SECONDS = 58
SHORT_WORDS = 80            # about 52 s at the Malayalam pace of ~0.65 s per word
SHORT_DISCLOSURE = "ഈ വീഡിയോയുടെ തിരക്കഥ AI സഹായത്തോടെ തയ്യാറാക്കിയതും ശബ്ദം കൃത്രിമവുമാണ്."


def build_short(short_dir: Path, long_items: list[list[dict]], out_dir: Path, work: Path, voice: dict,
                translate=translate_short, speak=None, mascot: str | None = None, cta: str | None = None) -> Path:
    """The Malayalam edition of one English Short (short_dir holds its script.json). Raises if it cannot be made to fit
    58 seconds or the translation stays unfaithful."""
    from autopilot import audio, shots
    from autopilot.render import render_short

    out_dir.mkdir(parents=True, exist_ok=True)
    short = json.loads((short_dir / "script.json").read_text())
    sp, wav, tp = out_dir / "script_ml.json", out_dir / "narration.wav", out_dir / "timings.json"
    speak = speak or (lambda s, w: make_voice({"sections": [{"heading": s["title"], "narration": s["narration"]}]}, w, voice))
    if not (sp.exists() and tp.exists() and wav.exists()):
        words = SHORT_WORDS
        for attempt in range(3):
            with ml_quota() if translate is translate_short else contextlib.nullcontext():
                ml = translate(short, words)
            timings = speak(ml, wav)
            if timings[-1]["end"] <= SHORT_MAX_SECONDS:
                break
            print(f"[ml] Short is {timings[-1]['end']:.0f}s, over {SHORT_MAX_SECONDS}s: asking for a shorter version", flush=True)
            wav.unlink(missing_ok=True)
            words = int(words * 0.8)
        else:
            raise OSError(f"the Malayalam Short is still over {SHORT_MAX_SECONDS}s")
        ml["section_index"] = short.get("section_index", 0)
        sp.write_text(json.dumps(ml, ensure_ascii=False, indent=1))
        tp.write_text(json.dumps(timings, ensure_ascii=False))
    ml, timings = json.loads(sp.read_text()), json.loads(tp.read_text())
    pool = shots.short_media_pool(long_items, ml.get("section_index", short.get("section_index", 0)))
    items = [{"kind": i["kind"], "path": Path(i["path"])} for i in pool if Path(i["path"]).exists()]
    music = audio.generate_ambient(timings[-1]["end"] + 3, out_dir / "music.wav", seed=int(short.get("section_index", 0)) + 1000)
    final = out_dir / "final.mp4"
    render_short(ml, timings, items, wav, final, work, music=music, look=ML_SHORT_CAPTIONS, mascot=mascot, cta=cta)
    return final


def short_description_ml(ml: dict, long_video_id: str | None, source_url: str | None, credits: list[str]) -> str:
    from autopilot import shorts

    hook = ml["narration"].split(". ")[0].rstrip(".") + "."
    text = shorts.short_description(hook, None, source_url, credits)
    text = text.replace("This video uses AI-assisted scripting and a synthetic voice.", SHORT_DISCLOSURE)
    if long_video_id:
        text = text.replace(hook, f"{hook}\n\nപൂർണ്ണ വീഡിയോ കാണുക: https://youtu.be/{long_video_id}", 1)
    return text


def run_daily_shorts(conn, cfg, long_job, src: Path, voice: dict, privacy: str, live: bool, build_only: bool,
                     retry: bool = False) -> list[str]:
    """Malayalam Shorts for today's video, one per English Short. Each is isolated: one failure does not stop the others."""
    from autopilot import notify, schedule, shorts, upload

    ml_cfg = cfg.malayalam or {}
    skip = "" if retry else _SKIP_FAILED.format(col="ml_status")
    rows = conn.execute("SELECT * FROM jobs WHERE kind = 'short' AND parent_id = ? AND video_id IS NOT NULL "
                        f"AND ml_video_id IS NULL AND COALESCE(ml_status, '') != 'built'{skip} ORDER BY short_idx",
                        (long_job["id"],)).fetchall()
    if not rows:
        return []
    long_row = conn.execute("SELECT ml_video_id, ml_publish_at FROM jobs WHERE id = ?", (long_job["id"],)).fetchone()
    if live and not build_only and not long_row["ml_video_id"]:
        return ["malayalam shorts: skipped (the Malayalam long video is not uploaded)"]
    items = json.loads((src / "items.json").read_text())
    credits = json.loads((src / "credits.json").read_text()) if (src / "credits.json").exists() else []
    source_url = json.loads((src / "script.json").read_text()).get("source_url")
    plans = json.loads((src / "shorts.json").read_text()) if (src / "shorts.json").exists() else []
    base = schedule.parse(long_row["ml_publish_at"]) if long_row["ml_publish_at"] else None
    offsets = ml_cfg.get("short_offsets_hours", [10, 15, 21])
    times = shorts.publish_times(len(rows), offsets, base) if base and privacy == "public" else [None] * len(rows)
    lines = []
    for row, when in zip(rows, times, strict=True):
        sdir = src / f"short{row['short_idx']}"
        if not (sdir / "script.json").exists() and row["short_idx"] < len(plans):     # rebuilt run: the plan holds the script
            sdir.mkdir(parents=True, exist_ok=True)
            (sdir / "script.json").write_text(json.dumps(plans[row["short_idx"]]))
        if not (sdir / "script.json").exists():
            lines.append(f"malayalam short {row['short_idx']}: skipped (its English files are gone)")
            continue
        try:
            final = build_short(sdir, items, sdir / "ml", Path("work") / "ml" / f"{src.name}-short{row['short_idx']}", voice,
                                mascot=mascot_style(cfg, short=True), cta=closing.SHORT_TAG["ml"] if cta_on(cfg, "short_tag") else None)
            if live and not build_only:
                ml = json.loads((sdir / "ml" / "script_ml.json").read_text())
                vid = upload.insert_video(final, f"{ml['title']} #Shorts",
                                          short_description_ml(ml, long_row["ml_video_id"], source_url, credits),
                                          ["shorts", "science", "malayalam", "ശാസ്ത്രം"], privacy=privacy, publish_at=when,
                                          profile="ml", language="ml")
                conn.execute("UPDATE jobs SET ml_video_id = ?, ml_publish_at = ?, ml_status = 'done' WHERE id = ?",
                             (vid, when, row["id"]))
                lines.append(f"Short {row['short_idx'] + 1}: https://youtu.be/{vid} goes public {ist_text(when)}")
                final.unlink(missing_ok=True)
            else:
                conn.execute("UPDATE jobs SET ml_status = 'built' WHERE id = ?", (row["id"],))
                lines.append(f"Short {row['short_idx'] + 1}: built, not uploaded")
            conn.commit()
        except Exception as exc:  # noqa: BLE001
            conn.execute("UPDATE jobs SET ml_status = ? WHERE id = ?", (f"failed: {type(exc).__name__}", row["id"]))
            conn.commit()
            lines.append(f"Short {row['short_idx'] + 1}: FAILED ({type(exc).__name__}: {str(exc)[:200]})")
    if lines:
        notify.send("Brightwork Malayalam Shorts:\n" + "\n".join(lines))
    return lines


def ist_text(ts: str | None) -> str:
    from autopilot.cli import ist

    return ist(ts)


# ---------- the daily Malayalam edition: build it, upload it to the Malayalam channel, remember it ----------
# A failed edition is skipped by the backup runs, so a real fault cannot repeat five times a day. The exception: "the models were out of quota
# or busy" (LLMUnavailable) says nothing about the edition itself, so the next run of the day tries again.
_SKIP_FAILED = " AND (COALESCE({col}, '') NOT LIKE 'failed%' OR {col} LIKE 'failed: LLMUnavailable%')"


def edition_due(conn, retry: bool = False):
    """The newest English long video that is uploaded and has no Malayalam edition yet. An edition that failed is retried
    only when asked (a manual run) or when it failed because the models were unavailable."""
    skip = "" if retry else _SKIP_FAILED.format(col="ml_status")
    return conn.execute(
        "SELECT * FROM jobs WHERE kind = 'long' AND video_id IS NOT NULL AND ml_video_id IS NULL "
        f"AND date(created_at) = date('now') AND COALESCE(ml_status, '') != 'built'{skip} ORDER BY id DESC LIMIT 1").fetchone()


def shorts_pending(conn, retry: bool = False):
    """Today's long video whose Malayalam edition is up but whose Malayalam Shorts are not all made."""
    skip = "" if retry else _SKIP_FAILED.format(col="s.ml_status")
    return conn.execute(
        "SELECT l.* FROM jobs l WHERE l.kind = 'long' AND l.ml_video_id IS NOT NULL AND date(l.created_at) = date('now') "
        "AND EXISTS (SELECT 1 FROM jobs s WHERE s.parent_id = l.id AND s.video_id IS NOT NULL AND s.ml_video_id IS NULL "
        f"AND COALESCE(s.ml_status, '') != 'built'{skip}) ORDER BY l.id DESC LIMIT 1").fetchone()


estimate_timings = shots_estimate_timings


def upload_edition(conn, job, out_dir: Path, src_dir: Path, hour_utc: int | None, privacy: str, live: bool) -> str | None:
    from autopilot import metadata, schedule, upload

    ml = json.loads((out_dir / "script_ml.json").read_text())
    timings = json.loads((out_dir / "timings.json").read_text())
    ml["chapters"] = metadata.chapter_marks(timings)
    credits = json.loads((src_dir / "credits.json").read_text()) if (src_dir / "credits.json").exists() else []
    description = metadata.build_description(ml, credits, disclosure="")   # the Malayalam description carries its own
    if not live:
        print(f"[ml] dry run: would upload {out_dir / 'final.mp4'} as {ml['title']!r}")
        return None
    publish_at = None
    if privacy == "public" and hour_utc is not None:
        publish_at = schedule.rfc3339(schedule.next_slot(hour_utc))
    vid = upload.insert_video(out_dir / "final.mp4", ml["title"], description, ml.get("tags", []), privacy=privacy,
                              publish_at=publish_at, profile="ml", language="ml")
    conn.execute("UPDATE jobs SET ml_video_id = ?, ml_publish_at = ?, ml_status = 'done' WHERE id = ?", (vid, publish_at, job["id"]))
    conn.commit()                                   # saved at once so a retry can never upload it twice
    try:
        upload.set_thumbnail(vid, out_dir / "thumbnail.jpg", profile="ml")
    except Exception as exc:  # noqa: BLE001 - best effort, as for the English channel
        print(f"[ml] thumbnail not set ({type(exc).__name__})", flush=True)
    return vid


def run_daily_edition(conn, cfg, privacy: str, live: bool, root: Path, retry: bool = False) -> str:
    """Called after the English daily run. Returns a status line. Never raises: the English video must not be affected."""
    from autopilot import notify, youtube_auth

    ml_cfg = cfg.malayalam or {}
    if not ml_cfg.get("enabled"):
        return "malayalam edition: disabled"
    build_only = live and not youtube_auth.configured("ml")   # no channel yet: still build it so it can be reviewed
    if not os.environ.get("GEMINI_API_KEY_ML"):
        return "malayalam edition: skipped (GEMINI_API_KEY_ML is not set)"
    job = edition_due(conn, retry)
    if not job:
        late = shorts_pending(conn, retry) if ml_cfg.get("shorts") else None
        if not late:
            return "malayalam edition: nothing due"
        return _only_shorts(conn, cfg, late, privacy, live, build_only, root, ml_cfg)
    src = next(iter(sorted(root.glob(f"{job['id']:04d}-*"))), None)
    if not src or not (src / "script.json").exists():
        return f"malayalam edition: skipped (the English script for job {job['id']} is gone)"
    voice = pick_ml_voice(job["id"], ml_cfg.get("voices"))
    try:
        build_edition(src, src / "ml", Path("work") / "ml" / src.name, voice, topic=job["topic"],
                      mascot=mascot_style(cfg, short=False), use_nasa=job["category"] == "space")
        vid = upload_edition(conn, job, src / "ml", src, ml_cfg.get("publish_hour_utc"), privacy, live and not build_only)
        if ml_cfg.get("shorts") and (vid or build_only):
            run_daily_shorts(conn, cfg, job, src, voice, privacy, live, build_only, retry)
        if build_only:
            conn.execute("UPDATE jobs SET ml_status = 'built' WHERE id = ?", (job["id"],))
            conn.commit()
            notify.send(f"Brightwork Malayalam: built the Malayalam edition of {job['topic']!r} but did not upload it "
                        "(no Malayalam channel login yet). Download it from this run's Artifacts.")
            return "malayalam edition: built, not uploaded (no Malayalam channel login yet)"
    except Exception as exc:  # noqa: BLE001
        conn.execute("UPDATE jobs SET ml_status = ? WHERE id = ?", (f"failed: {type(exc).__name__}", job["id"]))
        conn.commit()
        notify.send(f"Brightwork Malayalam: the Malayalam edition of {job['topic']!r} FAILED ({type(exc).__name__}: {str(exc)[:300]}). "
                    "The English video is unaffected.")
        return f"malayalam edition FAILED: {type(exc).__name__}: {exc}"
    if vid:
        (src / "ml" / "final.mp4").unlink(missing_ok=True)      # uploaded: the workflow keeps artifacts only for review builds
        at = conn.execute("SELECT ml_publish_at FROM jobs WHERE id = ?", (job["id"],)).fetchone()[0]
        from autopilot.cli import ist
        notify.send(f"Brightwork Malayalam: uploaded {json.loads((src / 'ml' / 'script_ml.json').read_text())['title']!r}\n"
                    f"https://youtu.be/{vid}\nGoes public: {ist(at)}\nVoice: {voice['name']}")
    return f"malayalam edition: done ({vid or 'dry run'})"


def redo_shorts(conn, now=None) -> list[str]:
    """Today's Malayalam Shorts are to be made again (for example after a timing fix). Each old one is deleted from the Malayalam
    channel and cleared from the job list so the next step rebuilds it, but ONLY while it is still private and scheduled: a Short that
    is already public is never touched. Returns what was done, one line per Short."""
    from datetime import datetime, timezone

    from autopilot import schedule, upload

    now = now or datetime.now(timezone.utc)
    long_job = conn.execute("SELECT id FROM jobs WHERE kind = 'long' AND ml_video_id IS NOT NULL AND date(created_at) = date('now') "
                            "ORDER BY id DESC LIMIT 1").fetchone()
    if not long_job:
        return ["redo: no Malayalam long video today"]
    lines = []
    rows = conn.execute("SELECT id, short_idx, ml_video_id FROM jobs WHERE parent_id = ? AND ml_video_id IS NOT NULL ORDER BY short_idx",
                        (long_job["id"],)).fetchall()
    yt = upload._client("ml")
    for r in rows:
        items = yt.videos().list(part="status", id=r["ml_video_id"]).execute().get("items", [])
        st = items[0]["status"] if items else None
        when = schedule.parse(st["publishAt"]) if st and st.get("publishAt") else None
        if st is not None and not (st["privacyStatus"] == "private" and when and when > now):
            lines.append(f"Short {r['short_idx'] + 1}: kept (already public or not scheduled)")
            continue
        if st is not None:
            upload.delete_video(r["ml_video_id"], "ml")
        conn.execute("UPDATE jobs SET ml_video_id = NULL, ml_publish_at = NULL, ml_status = NULL WHERE id = ?", (r["id"],))
        conn.commit()
        lines.append(f"Short {r['short_idx'] + 1}: old scheduled video deleted, will be rebuilt")
    return lines


def _only_shorts(conn, cfg, job, privacy: str, live: bool, build_only: bool, root: Path, ml_cfg: dict) -> str:
    """The Malayalam long video is up; make the Shorts that are still missing (a manual retry after a failure)."""
    src = next(iter(sorted(root.glob(f"{job['id']:04d}-*"))), None)
    if not src or not (src / "script.json").exists():
        return f"malayalam shorts: skipped (the English script for job {job['id']} is gone)"
    try:
        if not (src / "items.json").exists():
            recover_media(src, estimate_timings(json.loads((src / "script.json").read_text())), job["topic"],
                          use_nasa=job["category"] == "space")
        lines = run_daily_shorts(conn, cfg, job, src, pick_ml_voice(job["id"], ml_cfg.get("voices")), privacy, live, build_only,
                                 retry=True)
    except Exception as exc:  # noqa: BLE001
        return f"malayalam shorts FAILED: {type(exc).__name__}: {exc}"
    return "malayalam shorts: " + ("; ".join(lines) if lines else "nothing to do")
