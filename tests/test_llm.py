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
