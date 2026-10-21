import pytest

from autopilot import db
from autopilot.cli import done_count, ensure_progress


def test_ensure_progress_passes_when_a_video_finished():
    ensure_progress(2, 3)


def test_ensure_progress_exits_nonzero_when_nothing_finished(capsys):
    with pytest.raises(SystemExit) as exc:
        ensure_progress(2, 2)
    assert exc.value.code == 1 and "no video" in capsys.readouterr().err


def test_done_count(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    a = db.add_job(conn, "a", "long")
    db.add_job(conn, "b", "long")
    conn.execute("UPDATE jobs SET status = 'done' WHERE id = ?", (a,))
    assert done_count(conn) == 1


def _uploaded_job(conn, created="now", video_id="V", kind="long"):
    jid = db.add_job(conn, f"t{created}{video_id}", kind)
    conn.execute("UPDATE jobs SET video_id = ?, created_at = datetime(?) WHERE id = ?", (video_id, created, jid))
    conn.commit()


def test_uploaded_today_counts_only_todays_uploaded_long_videos(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    assert db.uploaded_today(conn) == 0
    _uploaded_job(conn, "now", "A")                      # today, uploaded: counts
    _uploaded_job(conn, "now", None)                     # today but never uploaded (dry run / failed): no
    _uploaded_job(conn, "now", "S", kind="short")        # a Short: no
    _uploaded_job(conn, "now", "B")
    conn.execute("UPDATE jobs SET created_at = datetime('now', '-2 days') WHERE video_id = 'B'")  # an old one: no
    conn.commit()
    assert db.uploaded_today(conn) == 1


def test_already_done_today_respects_the_daily_count(tmp_path):
    from autopilot.cli import already_done_today
    from autopilot.config import Config

    cfg = Config(niche="s", audience="en", formats={"long": {"per_day": 1}})
    conn = db.connect(tmp_path / "t.db")
    assert already_done_today(conn, cfg) is False
    _uploaded_job(conn, "now", "A")
    assert already_done_today(conn, cfg) is True
