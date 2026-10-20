import io
import json

import pytest

from autopilot import llm


class _Resp(io.BytesIO):
    pass


def _ok():
    body = {"candidates": [{"content": {"parts": [{"text": json.dumps({"a": 1})}]}}]}
    return _Resp(json.dumps(body).encode())


def test_retries_on_timeout_then_succeeds(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setattr(llm.time, "sleep", lambda s: None)
    calls = {"n": 0}

    def fake_urlopen(req, timeout):
        calls["n"] += 1
        if calls["n"] < 3:
            raise TimeoutError("read timed out")
        return _ok()

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    assert llm.generate_json("hi") == {"a": 1} and calls["n"] == 3


def test_gives_up_after_retries(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setattr(llm.time, "sleep", lambda s: None)
    monkeypatch.setattr(llm.urllib.request, "urlopen", lambda req, timeout: (_ for _ in ()).throw(TimeoutError()))
    with pytest.raises(llm.LLMError):
        llm.generate_json("hi", retries=2)


def _http_error(code, body=b"{}"):
    return llm.urllib.error.HTTPError("u", code, "x", {}, io.BytesIO(body))


def _quota_body(daily=True, delay="49581s"):
    viol = [{"quotaId": "GenerateRequestsPerDayPerProjectPerModel-FreeTier"}] if daily else []
    return json.dumps({"error": {"details": [{"violations": viol}, {"retryDelay": delay}]}}).encode()


def test_daily_quota_falls_through_to_next_model(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setenv("GEMINI_MODELS", "a,b")
    monkeypatch.setattr(llm, "_unavailable", set())
    monkeypatch.setattr(llm.time, "sleep", lambda s: None)
    seen = []

    def fake(req, timeout):
        seen.append(req.full_url.split("/models/")[1].split(":")[0])
        if seen[-1] == "a":
            raise _http_error(429, _quota_body())
        return _ok()

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake)
    assert llm.generate_json("hi") == {"a": 1} and seen == ["a", "b"]
    llm.generate_json("again")  # a is remembered as exhausted: goes straight to b
    assert seen == ["a", "b", "b"]


def test_short_rate_limit_waits_then_retries_same_model(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setenv("GEMINI_MODELS", "a,b")
    monkeypatch.setattr(llm, "_unavailable", set())
    sleeps, seen = [], []
    monkeypatch.setattr(llm.time, "sleep", sleeps.append)

    def fake(req, timeout):
        seen.append(req.full_url.split("/models/")[1].split(":")[0])
        if len(seen) == 1:
            raise _http_error(429, _quota_body(daily=False, delay="7s"))
        return _ok()

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake)
    assert llm.generate_json("hi") == {"a": 1} and seen == ["a", "a"] and sleeps == [8.0]


def test_all_models_exhausted_raises(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setenv("GEMINI_MODELS", "a,b")
    monkeypatch.setattr(llm, "_unavailable", set())
    monkeypatch.setattr(llm.urllib.request, "urlopen",
                        lambda req, timeout: (_ for _ in ()).throw(_http_error(429, _quota_body())))
    with pytest.raises(llm.LLMError):
        llm.generate_json("hi")


def test_overloaded_model_falls_through_without_being_remembered(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setenv("GEMINI_MODELS", "a,b")
    monkeypatch.setattr(llm, "_unavailable", set())
    monkeypatch.setattr(llm.time, "sleep", lambda s: None)

    def fake(req, timeout):
        if "/a:" in req.full_url:
            raise _http_error(503)
        return _ok()

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake)
    assert llm.generate_json("hi") == {"a": 1}
    assert "a" not in llm._unavailable  # 503 is temporary


def test_all_busy_raises_transient(monkeypatch):
    from autopilot.errors import TransientError

    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setenv("GEMINI_MODELS", "a")
    monkeypatch.setattr(llm, "_unavailable", set())
    monkeypatch.setattr(llm.time, "sleep", lambda s: None)
    monkeypatch.setattr(llm.urllib.request, "urlopen", lambda req, timeout: (_ for _ in ()).throw(_http_error(503)))
    with pytest.raises(TransientError):
        llm.generate_json("hi")


def _groq_ok(payload=None):
    body = {"choices": [{"message": {"content": json.dumps(payload or {"g": 1})}}]}
    return _Resp(json.dumps(body).encode())


def _setup(monkeypatch, groq=True):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setenv("GEMINI_MODELS", "gem")
    monkeypatch.delenv("GROQ_MODELS", raising=False)
    if groq:
        monkeypatch.setenv("GROQ_API_KEY", "gk")
        monkeypatch.setenv("GROQ_MODELS", "gq1,gq2")
    else:
        monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setattr(llm, "_unavailable", set())
    monkeypatch.setattr(llm.time, "sleep", lambda s: None)


def test_text_call_prefers_groq_and_never_touches_gemini(monkeypatch):
    _setup(monkeypatch)
    urls = []

    def fake(req, timeout):
        urls.append(req.full_url)
        return _groq_ok()

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake)
    assert llm.generate_json("hi") == {"g": 1}
    assert urls == [llm.GROQ_URL]


def test_vision_call_skips_groq(monkeypatch):
    _setup(monkeypatch)
    urls = []

    def fake(req, timeout):
        urls.append(req.full_url)
        return _ok()

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake)
    assert llm.generate_json("hi", images=[b"\xff\xd8"]) == {"a": 1}
    assert len(urls) == 1 and "generativelanguage" in urls[0]


def test_groq_daily_quota_moves_to_next_groq_model_then_gemini(monkeypatch):
    _setup(monkeypatch)
    seen = []

    def fake(req, timeout):
        seen.append(req.full_url if "groq" in req.full_url else "gemini")
        if "groq" in req.full_url:
            raise llm.urllib.error.HTTPError("u", 429, "x", {}, io.BytesIO(b'{"error": {"message": "tokens per day (TPD) limit"}}'))
        return _ok()

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake)
    assert llm.generate_json("hi") == {"a": 1}
    assert seen == [llm.GROQ_URL, llm.GROQ_URL, "gemini"]  # gq1 and gq2 both exhausted, then Gemini
    assert llm._unavailable == {"groq:gq1", "groq:gq2"}


def test_groq_per_minute_limit_waits_retry_after_then_succeeds(monkeypatch):
    _setup(monkeypatch)
    sleeps, n = [], {"c": 0}
    monkeypatch.setattr(llm.time, "sleep", sleeps.append)

    def fake(req, timeout):
        n["c"] += 1
        if n["c"] == 1:
            raise llm.urllib.error.HTTPError("u", 429, "x", {"retry-after": "12"}, io.BytesIO(b'{"error": {"message": "tokens per minute"}}'))
        return _groq_ok()

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake)
    assert llm.generate_json("hi") == {"g": 1} and sleeps == [13.0] and n["c"] == 2


def test_groq_413_falls_through_without_being_remembered(monkeypatch):
    _setup(monkeypatch)

    def fake(req, timeout):
        if "groq" in req.full_url:
            raise llm.urllib.error.HTTPError("u", 413, "x", {}, io.BytesIO(b"{}"))
        return _ok()

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake)
    assert llm.generate_json("hi") == {"a": 1} and llm._unavailable == set()


def test_gemini_only_when_no_groq_key(monkeypatch):
    _setup(monkeypatch, groq=False)
    urls = []

    def fake(req, timeout):
        urls.append(req.full_url)
        return _ok()

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake)
    llm.generate_json("hi")
    assert "generativelanguage" in urls[0]
