"""LLM client returning parsed JSON. Text calls try Groq first (1,000 requests/day free), then Gemini;
vision calls go to Gemini only. Each model has its own quota pool, so a daily-quota 429 moves on to the
next one; a short per-minute 429 just waits."""
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
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODELS = ["openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b"]
UA = {"User-Agent": "channel-autopilot/0.1 (https://github.com/NanduSav-1004/channel-autopilot)"}
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


_busy_until: dict[str, float] = {}
BUSY_SKIP = 600     # seconds
_unavailable: set[str] = set()  # per process: models already known to be exhausted


def _gemini_models(model: str | None) -> list[str]:
    if model:
        return [model]
    env = os.environ.get("GEMINI_MODELS")
    return [m.strip() for m in env.split(",") if m.strip()] if env else DEFAULT_MODELS


def _groq_models() -> list[str]:
    if not os.environ.get("GROQ_API_KEY"):
        return []
    env = os.environ.get("GROQ_MODELS")
    return [m.strip() for m in env.split(",") if m.strip()] if env else GROQ_MODELS


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


def _call_groq(model: str, prompt: str, key: str, retries: int) -> dict:
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}],
               "response_format": {"type": "json_object"}, "temperature": 0.8}
    if model.startswith("openai/gpt-oss"):
        payload["reasoning_effort"] = "low"  # fewer reasoning tokens: the free tier is token-limited
    body = json.dumps(payload).encode()
    for attempt in range(retries):
        req = urllib.request.Request(GROQ_URL, data=body, headers={
            **UA, "Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        wait = min(2 ** attempt * 2, 60)
        try:
            data = json.load(urllib.request.urlopen(req, timeout=240))
            return json.loads(data["choices"][0]["message"]["content"])
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                msg = exc.read().decode(errors="replace").lower()
                after = float(exc.headers.get("retry-after") or 30)
                if "per day" in msg or after > MAX_WAIT:
                    raise ModelUnavailable(f"{model} daily quota exhausted") from exc
                wait = after + 1
            elif exc.code in (400, 413):
                detail = exc.read().decode(errors="replace").replace("\n", " ")[:160]
                raise ModelBusy(f"{model} rejected the request (HTTP {exc.code}): {detail}") from exc
            elif exc.code in (401, 403, 404):
                raise ModelUnavailable(f"{model} HTTP {exc.code}") from exc
            elif exc.code not in RETRY_CODES:
                raise LLMError(f"Groq HTTP {exc.code}") from exc
            if attempt == retries - 1:
                raise ModelBusy(f"{model} HTTP {exc.code}") from exc
        except (KeyError, IndexError, json.JSONDecodeError) as exc:
            if attempt == retries - 1:
                raise ModelBusy(f"{model} bad response: {exc!r}") from exc
        except OSError as exc:
            if attempt == retries - 1:
                raise ModelBusy(f"{model} network error: {exc!r}") from exc
        time.sleep(wait)
    raise LLMError("unreachable")


def generate_json(
    prompt: str, model: str | None = None, retries: int = 4, images: list[bytes] | None = None
) -> dict:
    """`images` are JPEG bytes sent after the prompt text (vision tasks, Gemini only)."""
    gemini_key = os.environ.get("GEMINI_API_KEY")
    groq_key = os.environ.get("GROQ_API_KEY")
    if not gemini_key and not (groq_key and not images):
        raise LLMError("no API key set for this request (GEMINI_API_KEY, or GROQ_API_KEY for text)")
    attempts: list[tuple[str, str]] = []
    if not images and not model:
        attempts += [("groq", m) for m in _groq_models()]
    if gemini_key:
        gem = [("gemini", m) for m in _gemini_models(model)]
        attempts = gem + attempts if os.environ.get("LLM_PREFER") == "gemini" else attempts + gem  # a channel with its own key may go first
    parts = [{"text": prompt}] + [
        {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(b).decode()}}
        for b in images or []
    ]
    gem_body = json.dumps({
        "contents": [{"parts": parts}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.9},
    }).encode()
    for provider, m in attempts:
        if f"{provider}:{m}" in _unavailable or _busy_until.get(f"{provider}:{m}", 0) > time.time():
            continue
        try:
            if provider == "groq":
                return _call_groq(m, prompt, groq_key, retries)
            return _call(m, gem_body, gemini_key, retries)
        except ModelUnavailable as exc:
            _unavailable.add(f"{provider}:{m}")
            print(f"[llm] {provider}:{m} unavailable: {exc}", flush=True)
        except ModelBusy as exc:
            _busy_until[f"{provider}:{m}"] = time.time() + BUSY_SKIP   # do not wait on an overloaded model again straight away
            print(f"[llm] {provider}:{m} busy, trying next: {exc}", flush=True)
    raise LLMUnavailable("all LLM models are out of quota or busy")
