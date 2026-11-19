"""Science Chaya (Malayalam science explainers made with Claude, approved 2026-11-19): the fixed channel voice and its quota handling.

The voice is Gemini's "Puck" on the model gemini-3.1-flash-tts-preview. The same voice NAME sounds different on other models, so the model stays fixed.
Free quota is per model per key (project), so when one key runs out the SAME model and voice are tried with the next key (the owner allowed using the
keys of all three channels). Only when every key is out is another model tried, and the narration is then redone whole, so one video never mixes voices."""
import os
import wave
from pathlib import Path

from autopilot import malayalam, tts

VOICE = "Puck"
MODEL = "gemini-3.1-flash-tts-preview"
KEY_ENVS = ("GEMINI_API_KEY_ML", "GEMINI_API_KEY", "GEMINI_API_KEY_DATA")
FALLBACK_MODELS = ("gemini-3.8-flash-tts", "gemini-3.8-flash-lite-tts")


def engine_for(key_env: str, model: str = MODEL):
    """A Malayalam Gemini engine for one key and one model (the key's environment variable name is the class attribute the engine reads)."""
    cls = type("ChayaEngine", (malayalam.MalayalamGeminiEngine,), {"key_env": key_env})
    return cls(VOICE, [model])


def speak(script: dict, out_wav: Path, log=print) -> list[dict]:
    """The narration of `script` ({"sections": [{"heading", "narration"}]}) in the channel voice, with per-sentence timings. Tries every key on the
    fixed model first, then the fallback models."""
    last: Exception | None = None
    for model in (MODEL, *FALLBACK_MODELS):
        for key_env in KEY_ENVS:
            if not os.environ.get(key_env):
                continue
            try:
                timings = tts.synthesize_script(script, out_wav, engine_for(key_env, model), None)
                log(f"[chaya] voice {VOICE} on {model} with {key_env}")
                return timings
            except OSError as exc:
                last = exc
                log(f"[chaya] {model} with {key_env} could not speak it ({str(exc)[:90]}); trying the next")
    raise OSError(f"no key and model could speak the narration: {last}")


def wav_seconds(path: Path) -> float:
    with wave.open(str(path)) as w:
        return w.getnframes() / w.getframerate()
