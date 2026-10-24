"""Malayalam edition of a finished English video: translated script, Malayalam voice and captions, the same media.

Everything here uses its OWN Gemini key (GEMINI_API_KEY_ML, a separate free-tier project) so the English channel's
daily quota is never touched. Translation uses Gemini only: the Groq models produced garbled Malayalam."""
import json
import os
import re
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

META_PROMPT = """Translate this YouTube video's metadata into Malayalam for a Kerala audience.
- title: natural and curiosity-driven, at most 70 characters, keep the main keyword (English terms may stay in English).
- thumbnail_text: 2-4 punchy words for the thumbnail, Malayalam script.
- description: 2-3 sentences, then a new paragraph exactly: "ഈ വീഡിയോയുടെ തിരക്കഥ AI സഹായത്തോടെ തയ്യാറാക്കിയതും ശബ്ദം കൃത്രിമവുമാണ്."
- tags: 10-15 tags mixing Malayalam and English search terms.
Return JSON {{"title": str, "thumbnail_text": str, "description": str, "tags": [str]}}.

Title: {title}
Thumbnail text: {thumb}
Description: {description}"""


def translate_script(script: dict, gen: Callable[[str], dict] = llm.generate_json) -> dict:
    """The Malayalam script: same sections, same order, translated. Raises LLMError if a section cannot be translated."""
    sections = []
    for sec in script["sections"]:
        out = gen(SECTION_PROMPT.format(heading=sec["heading"], narration=sec["narration"]))
        narration = str(out["narration"]).strip()
        if not narration:
            raise llm.LLMError("empty translation")
        sections.append({"heading": str(out.get("heading", sec["heading"])).strip(), "narration": narration})
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
        pcm = self._speak(" ".join(sentences))
        pcm, spans = align_by_silence(sentences, pcm, 24000)
        return pcm, 24000, spans


def pick_ml_voice(video_number: int) -> dict:
    return tts.pick_voice(video_number, ML_VOICES)


def make_voice(script_ml: dict, out_wav: Path, voice: dict) -> list[dict]:
    return tts.synthesize_script(script_ml, out_wav, MalayalamGeminiEngine(voice["name"]), None)


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
    render_photo_video(ml, timings, items, shots.plan_cuts(timings, [len(s) for s in items]), wav, final, work,
                       music=music, look=ML_CAPTIONS)
    images = [i["path"] for sec in items for i in sec if i["kind"] == "image"]
    thumbnail.make_thumbnail(ml, images, out_dir / "thumbnail.jpg", lang="ml")
    return final
