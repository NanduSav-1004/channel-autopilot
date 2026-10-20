"""Gemini REST client (free tier) with retry/backoff. Returns parsed JSON."""
import base64
import json
import os
import time
import urllib.error
import urllib.request

ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
DEFAULT_MODEL = "gemini-flash-latest"
RETRY_CODES = {429, 500, 502, 503, 504}


class LLMError(RuntimeError):
    pass


def generate_json(
    prompt: str, model: str | None = None, retries: int = 5, images: list[bytes] | None = None
) -> dict:
    """`images` are JPEG bytes sent after the prompt text, for vision tasks."""
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise LLMError("GEMINI_API_KEY is not set")
    url = ENDPOINT.format(model=model or os.environ.get("GEMINI_MODEL", DEFAULT_MODEL))
    parts = [{"text": prompt}] + [
        {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(b).decode()}}
        for b in images or []
    ]
    body = json.dumps({
        "contents": [{"parts": parts}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.9},
    }).encode()
    for attempt in range(retries):
        req = urllib.request.Request(
            url, data=body, headers={"x-goog-api-key": key, "Content-Type": "application/json"}
        )
        try:
            data = json.load(urllib.request.urlopen(req, timeout=240))
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)
        except urllib.error.HTTPError as exc:
            if exc.code not in RETRY_CODES or attempt == retries - 1:
                raise LLMError(f"Gemini HTTP {exc.code}") from exc
        except (KeyError, IndexError, json.JSONDecodeError) as exc:
            if attempt == retries - 1:
                raise LLMError(f"bad Gemini response: {exc!r}") from exc
        except OSError as exc:  # timeouts, connection resets, DNS (URLError is an OSError)
            if attempt == retries - 1:
                raise LLMError(f"network error: {exc!r}") from exc
        time.sleep(min(2 ** attempt * 2, 60))
    raise LLMError("unreachable")
