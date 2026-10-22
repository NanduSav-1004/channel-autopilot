"""Text to speech with swappable engines (Piper or Kokoro, both offline, CPU). Synthesizes per sentence so caption
timings are exact."""
import re
import wave
from pathlib import Path

SENTENCE_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'(])")
SENTENCE_PAUSE = 0.22
SECTION_PAUSE = 0.6
PIPER_MODEL = "models/en_US-lessac-medium.onnx"
KOKORO_MODEL, KOKORO_VOICES = "models/kokoro-v1.0.int8.onnx", "models/voices-v1.0.bin"


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


def make_engine(settings: dict | None = None):
    """Build the engine named in config (`audio:` section). Falls back to Piper if Kokoro is unavailable, so a
    missing model file can never stop the daily video."""
    s = settings or {}
    if s.get("voice_engine", "piper") == "kokoro":
        try:
            return KokoroEngine(s.get("voice_name", "af_heart"), float(s.get("voice_speed", 1.12)))
        except (ImportError, OSError, ValueError) as exc:
            print(f"[tts] Kokoro unavailable ({type(exc).__name__}: {exc}); falling back to Piper", flush=True)
    return PiperEngine()


def synthesize_script(script: dict, out_wav: str | Path, engine=None) -> list[dict]:
    """Write one narration WAV; return per-section timings:
    [{"heading", "start", "end", "sentences": [{"text", "start", "end"}]}]."""
    engine = engine or PiperEngine()
    out_wav = Path(out_wav)
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    timings, t = [], 0.0
    with wave.open(str(out_wav), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        rate = None

        def silence(seconds: float) -> None:
            wav.writeframes(b"\x00\x00" * int(rate * seconds))

        for section in script["sections"]:
            sec = {"heading": section["heading"], "start": t, "sentences": []}
            for sentence in split_sentences(section["narration"]):
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
            sec["end"] = t
            timings.append(sec)
    return timings
