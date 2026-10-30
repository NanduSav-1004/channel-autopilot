import sqlite3
import sys

from autopilot import notify


def test_send_is_a_silent_no_op_without_config(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    assert notify.send("hi") is False


def test_send_posts_to_telegram_and_never_raises(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:abc")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "42")
    seen = {}

    class Resp:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self, *a): return b'{"ok": true}'

    def fake(req, timeout):
        seen["url"], seen["body"] = req.full_url, req.data.decode()
        return Resp()

    monkeypatch.setattr(notify.urllib.request, "urlopen", fake)
    assert notify.send("hello there") is True
    assert seen["url"].endswith("/bot123:abc/sendMessage") and "chat_id=42" in seen["body"] and "hello+there" in seen["body"]

    def boom(req, timeout):
        raise OSError("network down")

    monkeypatch.setattr(notify.urllib.request, "urlopen", boom)
    assert notify.send("x") is False


def test_watchdog_counts_todays_long_uploads(tmp_path):
    sys.path.insert(0, "scripts")
    import watchdog

    db = tmp_path / "a.db"
    c = sqlite3.connect(db)
    c.execute("CREATE TABLE jobs (kind TEXT, video_id TEXT, created_at TEXT)")
    c.execute("INSERT INTO jobs VALUES ('long', NULL, datetime('now'))")
    c.execute("INSERT INTO jobs VALUES ('long', 'abc', datetime('now', '-2 days'))")
    c.commit()
    assert watchdog.uploaded_today(str(db)) == 0
    c.execute("INSERT INTO jobs VALUES ('long', 'xyz', datetime('now'))")
    c.commit()
    assert watchdog.uploaded_today(str(db)) == 1


def test_ist_formats_indian_time_and_utc():
    from autopilot.cli import ist

    assert ist("2026-10-24T18:00:00Z") == "24 Oct 11:30 PM IST (18:00 UTC)"
    assert ist("2026-10-25T02:00:00Z") == "25 Oct 7:30 AM IST (02:00 UTC)"
    assert ist(None) == "immediately"


def test_the_watchdog_counts_todays_shorts_in_both_languages(tmp_path):
    sys.path.insert(0, "scripts")
    import watchdog

    c = sqlite3.connect(tmp_path / "a.db")
    c.execute("CREATE TABLE jobs (id INTEGER PRIMARY KEY, kind TEXT, video_id TEXT, created_at TEXT, parent_id INTEGER, ml_video_id TEXT)")
    c.execute("INSERT INTO jobs (kind, video_id, created_at) VALUES ('long', 'V', datetime('now'))")
    for i in range(2):
        c.execute("INSERT INTO jobs (kind, video_id, created_at, parent_id, ml_video_id) VALUES ('short', ?, datetime('now'), 1, ?)", (f"S{i}", f"M{i}"))
    c.commit()
    assert "English Shorts 2/3" in watchdog.shorts_missing(str(tmp_path / "a.db")) and "Malayalam Shorts 2/3" in watchdog.shorts_missing(str(tmp_path / "a.db"))
    c.execute("INSERT INTO jobs (kind, video_id, created_at, parent_id, ml_video_id) VALUES ('short', 'S9', datetime('now'), 1, 'M9')")
    c.commit()
    assert watchdog.shorts_missing(str(tmp_path / "a.db")) is None
