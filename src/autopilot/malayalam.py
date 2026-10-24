"""Malayalam edition of a finished English video: translated script, Malayalam voice and captions, the same media.

Everything here uses its OWN Gemini key (GEMINI_API_KEY_ML, a separate free-tier project) so the English channel's
daily quota is never touched. Translation uses Gemini only: the Groq models produced garbled Malayalam."""
import itertools
import json
import os
import re
import wave
from collections.abc import Callable
from contextlib import contextmanager
from pathlib import Path

import numpy as np

from autopilot import llm, tts

TRANSLATE_MODELS = "gemini-3.5-flash,gemini-3.1-flash-lite"
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

CHECK_PROMPT = """You check a Malayalam translation of a science explainer's narration against the English original.
List only SUBSTANTIVE problems: a number, date, name, unit or fact that differs from the English; a claim that is in the
Malayalam but not the English; a meaning that is reversed or distorted; an important sentence of the English that is missing.
Differences of style, word choice, sentence splitting or the use of English technical terms are fine and must NOT be listed.
Return JSON {{"issues": [str]}} (an empty list when the translation is faithful). Describe each issue in English.

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

META_PROMPT = """Translate this YouTube video's metadata into Malayalam for a Kerala audience.
- title: natural and curiosity-driven, at most 70 characters, keep the main keyword (English terms may stay in English).
- thumbnail_text: 2-4 punchy words for the thumbnail, Malayalam script.
- description: 2-3 sentences, then a new paragraph exactly: "ഈ വീഡിയോയുടെ തിരക്കഥ AI സഹായത്തോടെ തയ്യാറാക്കിയതും ശബ്ദം കൃത്രിമവുമാണ്."
- tags: 10-15 tags mixing Malayalam and English search terms.
Return JSON {{"title": str, "thumbnail_text": str, "description": str, "tags": [str]}}.

Title: {title}
Thumbnail text: {thumb}
Description: {description}"""


NUMBER_RE = re.compile(r"\d[\d,.]*\d|\d")
REPAIR_ROUNDS = 2


class TranslationRejected(RuntimeError):
    """The Malayalam still disagrees with the English after repairs: the edition is not published."""


def missing_numbers(english: str, malayalam: str) -> list[str]:
    """Numbers written in the English that do not appear in the Malayalam (digits must be kept as digits)."""
    have = set(NUMBER_RE.findall(malayalam))
    return sorted({n for n in NUMBER_RE.findall(english) if n not in have})


def check_translation(english: str, malayalam: str, gen: Callable[[str], dict]) -> list[str]:
    """Problems found, in English: numbers that went missing (exact check) plus what the model reviewer reports."""
    issues = [f"the number {n} from the English is missing" for n in missing_numbers(english, malayalam)]
    try:
        reported = [str(i) for i in gen(CHECK_PROMPT.format(english=english, malayalam=malayalam)).get("issues", [])]
        if reported:     # a second look filters the reviewer's own false alarms
            real = gen(VERIFY_PROMPT.format(english=english, malayalam=malayalam,
                                            issues="\n".join(f"{i + 1}. {r}" for i, r in enumerate(reported)))).get("real", [])
            if len(real) != len(reported):
                real = [True] * len(reported)
            issues += [r for r, ok in zip(reported, real, strict=True) if ok is True]
    except (llm.LLMError, KeyError, TypeError, ValueError, AttributeError):
        pass     # the exact checks above still applied; a reviewer outage must not block the edition
    return issues


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


def _letters(sentence: str) -> int:
    return max(1, sum(c.isalnum() or "഻" <= c <= "്" for c in sentence))   # consonants, vowels, and Malayalam signs


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
        pcm, spans = align_by_silence(sentences, pcm, 24000)
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
            parts = phrases(sent["text"])
            inside = [g for g in gaps if s0 < (g[0] + g[1]) / 2 < s1]
            psp = segment_by_pauses([_letters(x) for x in parts], inside, s0, s1)
            words = []
            for part, span in zip(parts, psp, strict=True):
                words += words_in(span, part.split())
            sent["start"], sent["end"], sent["words"] = round(s0, 3), round(s1, 3), words
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


def build_edition(src_dir: Path, out_dir: Path, work: Path, voice: dict, translate=translate_script) -> Path:
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
    items = shots.fill_sparse_sections([[{"kind": i["kind"], "path": Path(i["path"])} for i in sec]
                                        for sec in json.loads((src_dir / "items.json").read_text())])
    music = audio.generate_ambient(timings[-1]["end"] + 5, out_dir / "music.wav", seed=1)
    final = out_dir / "final.mp4"
    en_total = json.loads((src_dir / "timings.json").read_text())[-1]["end"] if (src_dir / "timings.json").exists() else 0
    cut = shots.CUT_SECONDS * max(1.0, timings[-1]["end"] / en_total) if en_total else shots.CUT_SECONDS
    plan = shots.plan_cuts(timings, [len(s) for s in items], cut_seconds=cut)   # longer audio, same number of shots
    render_photo_video(ml, timings, items, plan, wav, final, work,
                       music=music, look=ML_CAPTIONS)
    images = [i["path"] for sec in items for i in sec if i["kind"] == "image"]
    thumbnail.make_thumbnail(ml, images, out_dir / "thumbnail.jpg", lang="ml")
    return final


# ---------- the daily Malayalam edition: build it, upload it to the Malayalam channel, remember it ----------
def edition_due(conn):
    """The newest English long video that is uploaded and has no Malayalam edition yet (and none failed today)."""
    return conn.execute(
        "SELECT * FROM jobs WHERE kind = 'long' AND video_id IS NOT NULL AND ml_video_id IS NULL "
        "AND date(created_at) = date('now') AND COALESCE(ml_status, '') NOT LIKE 'failed%' AND COALESCE(ml_status, '') != 'built' ORDER BY id DESC LIMIT 1").fetchone()


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


def run_daily_edition(conn, cfg, privacy: str, live: bool, root: Path) -> str:
    """Called after the English daily run. Returns a status line. Never raises: the English video must not be affected."""
    from autopilot import notify, youtube_auth

    ml_cfg = cfg.malayalam or {}
    if not ml_cfg.get("enabled"):
        return "malayalam edition: disabled"
    build_only = live and not youtube_auth.configured("ml")   # no channel yet: still build it so it can be reviewed
    if not os.environ.get("GEMINI_API_KEY_ML"):
        return "malayalam edition: skipped (GEMINI_API_KEY_ML is not set)"
    job = edition_due(conn)
    if not job:
        return "malayalam edition: nothing due"
    src = next(iter(sorted(root.glob(f"{job['id']:04d}-*"))), None)
    if not src or not (src / "items.json").exists():
        return f"malayalam edition: skipped (the English files for job {job['id']} are gone)"
    voice = pick_ml_voice(job["id"], ml_cfg.get("voices"))
    try:
        build_edition(src, src / "ml", Path("work") / "ml" / src.name, voice)
        vid = upload_edition(conn, job, src / "ml", src, ml_cfg.get("publish_hour_utc"), privacy, live and not build_only)
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
