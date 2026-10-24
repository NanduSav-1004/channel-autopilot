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
