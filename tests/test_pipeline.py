from autopilot import db
from autopilot.pipeline import STAGES, run_pending


def _conn(tmp_path):
    return db.connect(tmp_path / "t.db")


def test_job_completes_when_all_stages_succeed(tmp_path):
    conn = _conn(tmp_path)
    db.add_job(conn, "how lasers work", "long")
    run_pending(conn, {s: (lambda job: None) for s in STAGES})
    row = conn.execute("SELECT * FROM jobs").fetchone()
    assert row["status"] == "done" and row["stage"] == "upload"


def test_failure_is_recorded_and_does_not_block_other_jobs(tmp_path):
    conn = _conn(tmp_path)
    bad = db.add_job(conn, "bad", "long")
    db.add_job(conn, "good", "short")

    def script(job):
        if job["id"] == bad:
            raise RuntimeError("boom")

    handlers = {s: (lambda job: None) for s in STAGES}
    handlers["script"] = script
    run_pending(conn, handlers)
    rows = {r["topic"]: r for r in conn.execute("SELECT * FROM jobs")}
    assert rows["bad"]["attempts"] == 3 and rows["bad"]["status"] == "failed"
    assert "boom" in rows["bad"]["error"]
    assert rows["good"]["status"] == "done"


def test_job_marked_failed_after_max_attempts(tmp_path):
    conn = _conn(tmp_path)
    db.add_job(conn, "bad", "long")
    handlers = {"script": lambda job: (_ for _ in ()).throw(RuntimeError("x"))}
    for _ in range(3):
        run_pending(conn, handlers)
    assert conn.execute("SELECT status FROM jobs").fetchone()["status"] == "failed"


def test_flaky_job_succeeds_on_retry_within_one_run(tmp_path):
    conn = _conn(tmp_path)
    db.add_job(conn, "flaky", "long")
    calls = {"n": 0}

    def script(job):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("transient")

    handlers = {s: (lambda job: None) for s in STAGES}
    handlers["script"] = script
    run_pending(conn, handlers)
    row = conn.execute("SELECT * FROM jobs").fetchone()
    assert row["status"] == "done" and row["attempts"] == 1
