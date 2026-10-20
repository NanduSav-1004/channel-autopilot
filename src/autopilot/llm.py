"""Gemini REST client (free tier) with retry/backoff and model fallback. Returns parsed JSON.

The free tier caps requests per model per day, so a daily-quota 429 moves on to the next model
(each has its own pool); a short per-minute 429 just waits."""
import base64
import json
import os
import time
import urllib.error
import urllib.request

from autopilot.errors import TransientError

ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
# Order: fast models first. (3.7/3.8-flash have no free-tier quota; lite models are slower but have pools.)
DEFAULT_MODELS = ["gemini-3.5-flash", "gemini-3.6-flash", "gemini-3.1-flash-lite", "gemini-3.5-flash-lite"]
RETRY_CODES = {500, 502, 503, 504}
MAX_WAIT = 90  # a 429 asking us to wait longer than this is treated as a daily quota


class LLMError(RuntimeError):
    pass


class ModelUnavailable(LLMError):
    """This model is out of quota or does not exist; try the next one (and remember it)."""


class ModelBusy(LLMError):
    """Overloaded or unreachable right now; try the next model but do not remember it."""


class LLMUnavailable(LLMError, TransientError):
    """Every model is out of quota or overloaded. Retry on a later run."""


_unavailable: set[str] = set()  # per process: models already known to be exhausted


def _models(model: str | None) -> list[str]:
    if model:
        return [model]
    env = os.environ.get("GEMINI_MODELS")
    return [m.strip() for m in env.split(",") if m.strip()] if env else DEFAULT_MODELS


def _retry_delay(body: bytes) -> tuple[float, bool]:
    """(seconds to wait, is_daily_quota) from a 429 response body."""
    try:
        err = json.loads(body)["error"]
    except (ValueError, KeyError, TypeError):
        return 30.0, False
    delay, daily = 30.0, False
    for det in err.get("details", []):
        if "retryDelay" in det:
            delay = float(str(det["retryDelay"]).rstrip("s") or 30)
        for v in det.get("violations", []):
            daily = daily or "PerDay" in v.get("quotaId", "")
    return delay, daily or delay > MAX_WAIT


def _call(model: str, body: bytes, key: str, retries: int) -> dict:
    url = ENDPOINT.format(model=model)
    for attempt in range(retries):
        req = urllib.request.Request(url, data=body, headers={"x-goog-api-key": key, "Content-Type": "application/json"})
        wait = min(2 ** attempt * 2, 60)
        try:
            data = json.load(urllib.request.urlopen(req, timeout=240))
            return json.loads(data["candidates"][0]["content"]["parts"][0]["text"])
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise ModelUnavailable(f"{model} not found") from exc
            if exc.code == 429:
                delay, daily = _retry_delay(exc.read())
                if daily:
                    raise ModelUnavailable(f"{model} daily quota exhausted") from exc
                wait = delay + 1
            elif exc.code not in RETRY_CODES:
                raise LLMError(f"Gemini HTTP {exc.code}") from exc
            if attempt == retries - 1:
                raise ModelBusy(f"{model} HTTP {exc.code}") from exc
        except (KeyError, IndexError, json.JSONDecodeError) as exc:
            if attempt == retries - 1:
                raise LLMError(f"bad Gemini response: {exc!r}") from exc
        except OSError as exc:  # timeouts, connection resets, DNS (URLError is an OSError)
            if attempt == retries - 1:
                raise ModelBusy(f"{model} network error: {exc!r}") from exc
        time.sleep(wait)
    raise LLMError("unreachable")


def generate_json(
    prompt: str, model: str | None = None, retries: int = 4, images: list[bytes] | None = None
) -> dict:
    """`images` are JPEG bytes sent after the prompt text, for vision tasks."""
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise LLMError("GEMINI_API_KEY is not set")
    parts = [{"text": prompt}] + [
        {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(b).decode()}}
        for b in images or []
    ]
    body = json.dumps({
        "contents": [{"parts": parts}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.9},
    }).encode()
    for m in _models(model):
        if m in _unavailable:
            continue
        try:
            return _call(m, body, key, retries)
        except ModelUnavailable:
            _unavailable.add(m)
        except ModelBusy:
            continue
    raise LLMUnavailable("all Gemini models are out of quota or busy")
