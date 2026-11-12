import http.client
import io
import urllib.error
import urllib.request

import pytest

from autopilot import llm, net


class Raw:
    def __init__(self, body=b'{"a": 1}', boom=None):
        self.body, self.boom = body, boom
        self.status, self.headers = 200, {"x": "y"}

    def read(self):
        if self.boom:
            raise self.boom
        return self.body

    def close(self):
        pass


def test_a_dropped_connection_becomes_a_connection_error_the_existing_handlers_understand(monkeypatch):
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=30: Raw(boom=http.client.IncompleteRead(b"", 10)))
    with pytest.raises(OSError):
        net.urlopen("http://x")
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=30: (_ for _ in ()).throw(http.client.RemoteDisconnected("closed")))
    with pytest.raises(ConnectionError):
        net.urlopen("http://x")
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=30: (_ for _ in ()).throw(urllib.error.HTTPError("u", 429, "slow", {}, io.BytesIO(b"x"))))
    with pytest.raises(urllib.error.HTTPError):                      # HTTP errors still arrive as themselves (the callers read their status)
        net.urlopen("http://x")


def test_a_good_answer_reads_like_the_original(monkeypatch):
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=30: Raw())
    import json

    r = net.urlopen("http://x")
    assert r.status == 200 and r.headers == {"x": "y"} and json.load(r) == {"a": 1}
    with net.urlopen("http://x") as again:
        assert again.read() == b'{"a": 1}'


def test_the_llm_retries_after_a_dropped_connection_and_unwraps_list_answers(monkeypatch):
    calls = []

    def flaky(req, timeout=30):
        calls.append(1)
        return Raw(boom=http.client.IncompleteRead(b"", 5)) if len(calls) == 1 else Raw(
            b'{"candidates": [{"content": {"parts": [{"text": "{\\"ok\\": true}"}]}}]}')
    monkeypatch.setattr(urllib.request, "urlopen", flaky)
    monkeypatch.setattr(llm.time, "sleep", lambda s: None)
    assert llm._call("m", b"{}", "k", retries=3) == {"ok": True} and len(calls) == 2
    assert llm._object([{"a": 1}]) == {"a": 1} and llm._object([{"a": 1}, {"b": 2}]) == {"items": [{"a": 1}, {"b": 2}]}
    assert llm._object("text") == {} and llm._object({"k": 1}) == {"k": 1}


def test_the_failed_step_names_come_from_the_runs_job_list(monkeypatch):
    import json
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
    import ci_info

    body = json.dumps({"jobs": [{"steps": [{"name": "Set up job", "conclusion": "success"}, {"name": "System packages", "conclusion": "failure"},
                                            {"name": "Keepalive", "conclusion": "success"}]}]}).encode()
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=20: net.Response(body, 200, {}))
    monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
    monkeypatch.setenv("GITHUB_RUN_ID", "1")
    monkeypatch.setenv("GITHUB_TOKEN", "t")
    assert ci_info.failed_steps() == "System packages"
    monkeypatch.delenv("GITHUB_TOKEN")
    assert ci_info.failed_steps() == ""                                   # cannot be read: empty, never an exception
