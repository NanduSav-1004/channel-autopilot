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
