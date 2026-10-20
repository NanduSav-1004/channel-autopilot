"""Piper TTS (CPU, offline). Synthesizes per sentence so caption timings are exact."""
import re
import wave
from pathlib import Path

SENTENCE_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'(])")
SENTENCE_PAUSE = 0.25
SECTION_PAUSE = 0.7


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in SENTENCE_RE.split(text.strip()) if s.strip()]


def synthesize_script(script: dict, out_wav: str | Path, model: str = "models/en_US-lessac-medium.onnx") -> list[dict]:
    """Write one narration WAV; return per-section timings:
    [{"heading", "start", "end", "sentences": [{"text", "start", "end"}]}]."""
    from piper import PiperVoice  # imported lazily: heavy, and tests don't need it

    voice = PiperVoice.load(model)
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
                for chunk in voice.synthesize(sentence):
                    if rate is None:
                        rate = chunk.sample_rate
                        wav.setframerate(rate)
                    wav.writeframes(chunk.audio_int16_bytes)
                    t += len(chunk.audio_int16_bytes) / 2 / rate
                sec["sentences"].append({"text": sentence, "start": start, "end": t})
                silence(SENTENCE_PAUSE)
                t += SENTENCE_PAUSE
            silence(SECTION_PAUSE - SENTENCE_PAUSE)
            t += SECTION_PAUSE - SENTENCE_PAUSE
            sec["end"] = t
            timings.append(sec)
    return timings
