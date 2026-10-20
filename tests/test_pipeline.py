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


def test_transient_error_does_not_burn_attempts_and_stays_pending(tmp_path):
    from autopilot.errors import TransientError

    conn = _conn(tmp_path)
    db.add_job(conn, "outage", "long")

    def script(job):
        raise TransientError("gemini down")

    handlers = {s: (lambda job: None) for s in STAGES}
    handlers["script"] = script
    run_pending(conn, handlers)
    row = conn.execute("SELECT * FROM jobs").fetchone()
    assert row["status"] == "pending" and row["attempts"] == 0 and "will retry" in row["error"]


def test_restart_job_rewinds_to_start_without_counting_an_attempt(tmp_path):
    from autopilot.errors import RestartJob

    conn = _conn(tmp_path)
    jid = db.add_job(conn, "resume", "long")
    conn.execute("UPDATE jobs SET stage = 'voice' WHERE id = ?", (jid,))
    conn.commit()
    ran, state = [], {"restarted": False}

    def render(job):
        ran.append("render")
        if not state["restarted"]:
            state["restarted"] = True
            raise RestartJob("missing items.json")

    handlers = {s: (lambda job, s=s: ran.append(s)) for s in STAGES}
    handlers["render"] = render
    run_pending(conn, handlers)
    row = conn.execute("SELECT * FROM jobs").fetchone()
    assert row["status"] == "done" and row["attempts"] == 0
    assert ran[:3] == ["visuals", "render", "script"] and ran.count("script") == 1  # rewound to the very start


def test_restart_job_twice_is_a_failure_not_an_infinite_loop(tmp_path):
    from autopilot.errors import RestartJob

    conn = _conn(tmp_path)
    db.add_job(conn, "stuck", "long")
    calls = []

    def script(job):
        calls.append(1)
        raise RestartJob("missing forever")

    run_pending(conn, {"script": script})
    assert len(calls) <= 8 and conn.execute("SELECT status FROM jobs").fetchone()[0] == "failed"
