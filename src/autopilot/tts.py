"""Text to speech with swappable engines (Piper or Kokoro, both offline, CPU). Synthesizes per sentence so caption
timings are exact."""
import base64
import difflib
import io
import json
import os
import random
import re
import urllib.error
import urllib.request
import uuid
import wave
from pathlib import Path

SENTENCE_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'(])")
SENTENCE_PAUSE = 0.22
SECTION_PAUSE = 0.6
PIPER_MODEL = "models/en_US-lessac-medium.onnx"
KOKORO_MODEL, KOKORO_VOICES = "models/kokoro-v1.0.int8.onnx", "models/voices-v1.0.bin"


def estimate_word_times(text: str, start: float, end: float) -> list[dict]:
    """Spread a sentence's words over its time span, in proportion to how long each takes to say (letters, plus a little
    extra after a comma or colon where the voice pauses). Good enough to highlight words as they are spoken."""
    tokens = text.split()
    if not tokens:
        return []
    weights = [sum(c.isalnum() for c in w) + 2 + (3 if w[-1] in ",;:" else 0) for w in tokens]
    total, span, t, words = sum(weights), max(end - start, 0.0), start, []
    for w, wt in zip(tokens, weights, strict=True):
        dur = span * wt / total
        words.append({"w": w, "s": round(t, 3), "e": round(t + dur, 3)})
        t += dur
    return words


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in SENTENCE_RE.split(text.strip()) if s.strip()]


class PiperEngine:
    name = "piper"

    def __init__(self, model: str = PIPER_MODEL):
        from piper import PiperVoice  # imported lazily: heavy, and tests do not need it

        self.voice = PiperVoice.load(model)

    def synth(self, text: str) -> tuple[bytes, int]:
        chunks = list(self.voice.synthesize(text))
        return b"".join(c.audio_int16_bytes for c in chunks), chunks[0].sample_rate


class KokoroEngine:
    name = "kokoro"

    def __init__(self, voice: str = "af_heart", speed: float = 1.12, model: str = KOKORO_MODEL, voices: str = KOKORO_VOICES):
        from kokoro_onnx import Kokoro

        self.k, self.voice, self.speed = Kokoro(model, voices), voice, speed
        self.lang = "en-us" if voice[0] == "a" else "en-gb"

    def synth(self, text: str) -> tuple[bytes, int]:
        import numpy as np

        audio, rate = self.k.create(text, voice=self.voice, speed=self.speed, lang=self.lang)
        return (np.clip(audio, -1, 1) * 32767).astype("<i2").tobytes(), rate


GEMINI_TTS_MODELS = ["gemini-3.1-flash-tts-preview", "gemini-3.8-flash-tts", "gemini-3.8-flash-lite-tts",
                     "gemini-2.5-flash-preview-tts"]  # each model has its own free daily pool
GEMINI_STYLE = "Say this in an energetic, fast-paced, curious YouTube-explainer voice, with punchy emphasis:\n\n"
UA = {"User-Agent": "channel-autopilot/0.1 (https://github.com/NanduSav-1004/channel-autopilot)"}


def align_sentences(sentences: list[str], words: list[dict], total: float) -> list[tuple[float, float]]:
    """Sentence (start, end) times inside one section's audio. `words` are timed words from speech recognition
    (they may differ a little from the script), so each sentence boundary is placed where the same fraction of the
    letters has been spoken. With no words, fall back to a plain proportional split."""
    def letters(s: str) -> int:
        return sum(c.isalnum() for c in s) or 1

    total_letters = sum(letters(s) for s in sentences)
    cum, ends = 0, []
    if words:
        spoken, acc = [], 0
        for w in words:
            acc += letters(w.get("word", ""))
            spoken.append((acc, float(w["end"])))
        for s in sentences:
            cum += letters(s)
            target = cum / total_letters * acc
            ends.append(next((end for a, end in spoken if a >= target), spoken[-1][1]))
    else:
        for s in sentences:
            cum += letters(s)
            ends.append(cum / total_letters * total)
    ends[-1] = min(max(ends[-1], 0.0), total) if not words else ends[-1]
    starts = [0.0] + ends[:-1]
    return list(zip(starts, ends, strict=True))


def _whisper_words(wav: bytes, language: str = "en", model: str = "whisper-large-v3-turbo") -> list[dict]:
    """Word timestamps from Groq's free Whisper, or [] if unavailable (alignment then falls back to proportional)."""
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        return []
    b = uuid.uuid4().hex

    def field(n: str, v: str) -> bytes:
        return f'--{b}\r\nContent-Disposition: form-data; name="{n}"\r\n\r\n{v}\r\n'.encode()

    body = (field("model", model) + field("language", language) + field("response_format", "verbose_json")
            + field("timestamp_granularities[]", "word")
            + f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="a.wav"\r\nContent-Type: audio/wav\r\n\r\n'.encode()
            + wav + f"\r\n--{b}--\r\n".encode())
    req = urllib.request.Request("https://api.groq.com/openai/v1/audio/transcriptions", data=body, headers={
        **UA, "Authorization": f"Bearer {key}", "Content-Type": f"multipart/form-data; boundary={b}"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=120)).get("words", [])
    except (OSError, ValueError):
        return []


class GeminiEngine:
    """Expressive, directed voices (e.g. Sadachbia). Free tier: about 20 requests per day per model, and the audio
    has no timing, so a whole section is spoken in one request and its sentences are located with Whisper."""
    name = "gemini"
    whole_section = True
    key_env = "GEMINI_API_KEY"
    style: str | None = None          # None: the English direction (GEMINI_STYLE); subclasses for other languages override

    def __init__(self, voice: str = "Sadachbia"):
        self.voice = voice
        self.key = os.environ.get(self.key_env)
        if not self.key:
            raise OSError(f"{self.key_env} is not set")

    def _speak(self, text: str) -> bytes:
        body = json.dumps({"contents": [{"parts": [{"text": (GEMINI_STYLE if self.style is None else self.style) + text}]}], "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": self.voice}}}}}).encode()
        last = None
        for model in GEMINI_TTS_MODELS:
            req = urllib.request.Request(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent", data=body,
                headers={"x-goog-api-key": self.key, "Content-Type": "application/json"})
            try:
                data = json.load(urllib.request.urlopen(req, timeout=240))
                return base64.b64decode(data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
            except urllib.error.HTTPError as exc:  # quota, missing model, overload: try the next model's pool
                last = f"{model} HTTP {exc.code}"
            except (OSError, KeyError, IndexError, ValueError) as exc:
                last = f"{model} {type(exc).__name__}"
        raise OSError(f"all Gemini TTS models failed ({last})")

    def synth_section(self, sentences: list[str]) -> tuple[bytes, int, list[tuple[float, float]]]:
        pcm = self._speak(" ".join(sentences))
        rate = 24000
        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(rate)
            w.writeframes(pcm)
        words = _whisper_words(buf.getvalue())
        if not words:  # without a transcript we can neither locate the sentences nor prove the direction was not spoken
            raise OSError("Whisper unavailable: cannot verify the Gemini narration, so it is not used")
        pcm, words = strip_spoken_direction(pcm, rate, sentences[0], words)
        total = len(pcm) / 2 / rate
        return pcm, rate, align_sentences(sentences, words, total)


def strip_spoken_direction(pcm: bytes, rate: int, first_sentence: str, words: list[dict]) -> tuple[bytes, list[dict]]:
    """Gemini sometimes SPEAKS the style direction before the script. Find where the script's own first words begin in
    the transcript and cut the audio before that point. Raises OSError if the script text cannot be found at all."""
    want = [_norm(w) for w in first_sentence.split()[:4] if _norm(w)]
    heard = [_norm(h["word"]) for h in words]
    best_i, best_score = 0, 0.0
    for i in range(min(len(heard), 60)):                       # a spoken direction is at most a few dozen words
        window = heard[i:i + len(want)]
        score = difflib.SequenceMatcher(None, want, window, autojunk=False).ratio()
        if score > best_score + 1e-9:
            best_i, best_score = i, score
    if best_score < 0.6:
        raise OSError("the script text was not found in the spoken Gemini audio")
    offset = max(0.0, float(words[best_i]["start"]) - 0.06)
    if offset < 0.25:                                           # nothing but a normal breath before the first word
        return pcm, words
    print(f"[tts] Gemini spoke {best_i} extra word(s) before the script; cutting the first {offset:.1f}s", flush=True)
    cut = int(offset * rate) * 2
    shifted = [{**h, "start": float(h["start"]) - offset, "end": float(h["end"]) - offset} for h in words[best_i:]]
    return pcm[cut:], shifted


def pick_voice(root_id: int, voices: list[dict]) -> dict:
    """A random voice per video that never repeats the previous video's voice. Deterministic: the same video id
    always gets the same voice (so a long video and its Shorts match, and a retry does not change it)."""
    prev, chosen = None, voices[0]
    for i in range(1, max(1, root_id) + 1):
        candidates = [v for v in voices if v is not prev] if len(voices) > 1 else voices
        chosen = random.Random(i).choice(candidates)
        prev = chosen
    return chosen


def build_engine(spec: dict):
    if spec.get("engine") == "gemini":
        return GeminiEngine(spec.get("name", "Sadachbia"))
    if spec.get("engine") == "kokoro":
        return KokoroEngine(spec.get("name", "af_heart"), float(spec.get("speed", 1.12)))
    return PiperEngine()


def make_engine(settings: dict | None = None, root_id: int = 1):
    """Build the voice for a video from config (`audio:` section): a random pick from `voices` (never the same as the
    previous video's), else the single `voice_engine`. Any failure to start the chosen voice falls back to `fallback`
    and finally Piper, so a missing model or quota can never stop the daily video."""
    s = settings or {}
    voices = s.get("voices")
    if voices:
        spec = pick_voice(root_id, voices)
        print(f"[tts] voice for this video: {spec.get('engine')}:{spec.get('name')}", flush=True)
    elif s.get("voice_engine"):
        spec = {"engine": s["voice_engine"], "name": s.get("voice_name"), "speed": s.get("voice_speed", 1.12)}
    else:
        return PiperEngine()
    for candidate in (spec, s.get("fallback"), {"engine": "piper"}):
        if not candidate:
            continue
        try:
            return build_engine(candidate)
        except (ImportError, OSError, ValueError) as exc:
            print(f"[tts] {candidate.get('engine')}:{candidate.get('name')} unavailable ({type(exc).__name__}: {exc}); "
                  "trying the next option", flush=True)
    return PiperEngine()


def _norm(word: str) -> str:
    return re.sub(r"[^a-z0-9]", "", word.lower())


def _wav_slice(path: Path, start: float, end: float) -> bytes:
    """A WAV (as bytes) holding only [start, end] seconds of `path`."""
    with wave.open(str(path)) as w:
        rate = w.getframerate()
        w.setpos(min(w.getnframes(), max(0, int(start * rate))))
        frames = w.readframes(max(0, int((end - start) * rate)))
        buf = io.BytesIO()
        with wave.open(buf, "wb") as out:
            out.setnchannels(w.getnchannels())
            out.setsampwidth(w.getsampwidth())
            out.setframerate(rate)
            out.writeframes(frames)
    return buf.getvalue()


def refine_word_times(script_words: list[dict], heard: list[dict], lo: float, hi: float) -> list[dict]:
    """Replace estimated word times with the times Whisper heard, matching words by text. Words Whisper missed or
    heard differently are spread between their matched neighbours. Always monotonic and inside [lo, hi]."""
    if not script_words or not heard:
        return script_words
    a = [_norm(w["w"]) for w in script_words]
    b = [_norm(h["word"]) for h in heard]
    anchors: dict[int, tuple[float, float]] = {}
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            anchors[blk.a + k] = (float(heard[blk.b + k]["start"]), float(heard[blk.b + k]["end"]))
    if not anchors:
        return script_words
    n, starts, ends = len(script_words), [0.0] * len(script_words), [0.0] * len(script_words)
    known = sorted(anchors)
    for idx, (s, e) in anchors.items():
        starts[idx], ends[idx] = s, e
    for left, right in zip([-1, *known], [*known, n], strict=True):  # runs of unmatched words between anchors
        run = list(range(left + 1, right))
        if not run:
            continue
        t0 = ends[left] if left >= 0 else lo
        t1 = starts[right] if right < n else hi
        weights = [sum(c.isalnum() for c in script_words[k]["w"]) + 2 for k in run]
        t, total = t0, sum(weights)
        for k, wt in zip(run, weights, strict=True):
            starts[k], ends[k] = t, t + max(t1 - t0, 0.0) * wt / total
            t = ends[k]
    out, prev = [], lo
    for w, s, e in zip(script_words, starts, ends, strict=True):
        s = min(max(s, prev), hi)
        e = min(max(e, s + 0.03), hi)
        out.append({"w": w["w"], "s": round(s, 3), "e": round(e, 3)})
        prev = s
    return out


def add_word_times(out_wav: Path, timings: list[dict], whisper=None) -> None:
    """Give every sentence a `words` list with start/end times. Estimates first; then, one Whisper call per section,
    the real times. Whisper being unavailable just leaves the estimates."""
    whisper = whisper or _whisper_words
    for sec in timings:
        for sent in sec["sentences"]:
            sent["words"] = estimate_word_times(sent["text"], sent["start"], sent["end"])
        if not sec["sentences"]:
            continue
        lo, hi = max(0.0, sec["start"] - 0.15), sec["end"] + 0.15
        try:
            heard = whisper(_wav_slice(out_wav, lo, hi))
        except (OSError, wave.Error, ValueError):
            continue
        heard = [{"word": h["word"], "start": float(h["start"]) + lo, "end": float(h["end"]) + lo} for h in heard]
        flat = [w for sent in sec["sentences"] for w in sent["words"]]
        fixed = iter(refine_word_times(flat, heard, sec["sentences"][0]["start"], sec["sentences"][-1]["end"]))
        for sent in sec["sentences"]:
            sent["words"] = clamp_words([next(fixed) for _ in sent["words"]], sent["start"], sent["end"])


def clamp_words(words: list[dict], lo: float, hi: float) -> list[dict]:
    """Keep a sentence's words inside the sentence's exact span (known from synthesis), in order."""
    out, prev = [], lo
    for w in words:
        s = min(max(w["s"], prev, lo), max(lo, hi - 0.03))
        e = min(max(w["e"], s + 0.03), max(hi, s + 0.03))
        out.append({"w": w["w"], "s": round(s, 3), "e": round(e, 3)})
        prev = s
    return out


def synthesize_script(script: dict, out_wav: str | Path, engine=None, fallback=None) -> list[dict]:
    """Write one narration WAV; return per-section timings:
    [{"heading", "start", "end", "sentences": [{"text", "start", "end"}]}].
    If `engine` fails partway (for example a Gemini quota), the WHOLE script is redone with `fallback`, so one video
    never mixes two voices."""
    engine = engine or PiperEngine()
    used = engine
    try:
        timings = _synthesize(script, out_wav, engine)
    except (OSError, wave.Error) as exc:
        if fallback is None:
            raise
        print(f"[tts] {engine.name} failed ({exc}); redoing the whole narration with {fallback.name}", flush=True)
        timings = _synthesize(script, out_wav, fallback)
        used = fallback
    if getattr(used, "estimate_words_only", False):  # e.g. Malayalam: the Whisper refinement is English-only
        for sec in timings:
            for sent in sec["sentences"]:
                sent["words"] = estimate_word_times(sent["text"], sent["start"], sent["end"])
    else:
        add_word_times(Path(out_wav), timings)
    return timings


def _synthesize(script: dict, out_wav: str | Path, engine) -> list[dict]:
    out_wav = Path(out_wav)
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    timings, t = [], 0.0
    with wave.open(str(out_wav), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(24000)  # a placeholder so that closing a file the engine never wrote to cannot raise a
        rate = None              # different error and hide the real one (it is replaced by the true rate below)

        def silence(seconds: float) -> None:
            wav.writeframes(b"\x00\x00" * int(rate * seconds))

        for section in script["sections"]:
            sec = {"heading": section["heading"], "start": t, "sentences": []}
            sentences = getattr(engine, "splitter", split_sentences)(section["narration"])
            if getattr(engine, "whole_section", False):
                pcm, sr, spans = engine.synth_section(sentences)
                if rate is None:
                    rate = sr
                    wav.setframerate(rate)
                wav.writeframes(pcm)
                for text, (a, b) in zip(sentences, spans, strict=True):
                    sec["sentences"].append({"text": text, "start": t + a, "end": t + b})
                t += len(pcm) / 2 / rate
            else:
                for sentence in sentences:
                    start = t
                    pcm, sr = engine.synth(sentence)
                    if rate is None:
                        rate = sr
                        wav.setframerate(rate)
                    wav.writeframes(pcm)
                    t += len(pcm) / 2 / rate
                    sec["sentences"].append({"text": sentence, "start": start, "end": t})
                    silence(SENTENCE_PAUSE)
                    t += SENTENCE_PAUSE
                silence(SECTION_PAUSE - SENTENCE_PAUSE)
                t += SECTION_PAUSE - SENTENCE_PAUSE
            if getattr(engine, "whole_section", False):
                silence(SECTION_PAUSE)
                t += SECTION_PAUSE
            sec["end"] = t
            timings.append(sec)
    return timings
