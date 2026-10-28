import io
import urllib.error

import pytest

from autopilot import cli, wiki
from autopilot.errors import TransientError


def _http(code, retry_after=None):
    h = {"Retry-After": retry_after} if retry_after else {}
    return urllib.error.HTTPError("u", code, "x", h, io.BytesIO(b""))


def test_wikipedia_is_retried_on_429_and_timeouts_then_gives_up_with_oserror(monkeypatch):
    monkeypatch.setattr(wiki.time, "sleep", lambda s: None)
    calls = []

    def flaky(req, timeout):
        calls.append(1)
        if len(calls) < 3:
            raise _http(429, "1") if len(calls) == 1 else TimeoutError()
        return io.BytesIO(b'{"ok": 1}')

    monkeypatch.setattr(wiki.urllib.request, "urlopen", flaky)
    assert wiki._get({"a": 1}) == {"ok": 1} and len(calls) == 3

    monkeypatch.setattr(wiki.urllib.request, "urlopen", lambda r, timeout: (_ for _ in ()).throw(_http(503)))
    with pytest.raises(OSError, match="Wikipedia is not answering"):
        wiki._get({"a": 1})
    monkeypatch.setattr(wiki.urllib.request, "urlopen", lambda r, timeout: (_ for _ in ()).throw(_http(404)))
    with pytest.raises(urllib.error.HTTPError):               # a real 404 is not retried
        wiki._get({"a": 1})


def test_topic_discovery_waits_and_retries_after_a_transient_failure(monkeypatch):
    from autopilot.config import Config

    cfg = Config(niche="s", audience="a", formats={"long": {"min_source_chars": 10}})
    attempts = []

    def discover(conn, niche, want, *a, **kw):
        attempts.append(1)
        if len(attempts) < 3:
            raise TransientError("providers busy")
        return [7]

    monkeypatch.setattr(cli.topics, "discover_mix", discover)
    assert cli.discover_with_retries(None, cfg, 1, tries=3, pause=0) == [7] and len(attempts) == 3
    attempts.clear()
    monkeypatch.setattr(cli.topics, "discover_mix", lambda *a, **k: (_ for _ in ()).throw(OSError("down")))
    with pytest.raises(OSError):
        cli.discover_with_retries(None, cfg, 1, tries=2, pause=0)


def test_a_candidate_whose_wikipedia_fetch_fails_is_skipped_not_fatal(tmp_path):
    from autopilot import db, topics

    conn = db.connect(tmp_path / "x.db")
    gen = lambda p: {"topics": [{"topic": "A", "wikipedia_title": "A", "search_query": "a"},
                                {"topic": "B", "wikipedia_title": "B", "search_query": "b"}]}

    def fetch(title):
        if title == "A":
            raise OSError("Wikipedia is not answering")
        return {"title": "B", "url": "u", "text": "x" * 100}

    ids = topics.discover(conn, "science", 1, gen=gen, fetch=fetch, min_source_chars=10, score=lambda q: 0.0)
    assert len(ids) == 1


def test_underscore_style_wikipedia_titles_are_accepted(tmp_path):
    from autopilot import db, topics

    conn = db.connect(tmp_path / "x.db")
    gen = lambda p: {"topics": [{"topic": "Solar panels", "wikipedia_title": "Photovoltaic_system", "search_query": "how solar panels work"}]}
    fetch = lambda title: {"title": "Photovoltaic system", "url": "u", "text": "x" * 100}
    assert len(topics.discover(conn, "science", 1, gen=gen, fetch=fetch, min_source_chars=10, score=lambda q: 1.0)) == 1


def test_discovery_asks_again_when_every_candidate_is_rejected(monkeypatch):
    from autopilot.config import Config

    cfg = Config(niche="s", audience="a", formats={"long": {"min_source_chars": 10}})
    answers = [[], [], [9]]
    monkeypatch.setattr(cli.topics, "discover_mix", lambda *a, **k: answers.pop(0))
    assert cli.discover_with_retries(None, cfg, 1, tries=3, pause=0) == [9]
