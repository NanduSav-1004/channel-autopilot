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
