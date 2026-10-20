"""Stage runner: each stage is idempotent; failures are recorded and never block the queue."""
import sqlite3
import time
from collections.abc import Callable

# Ordered pipeline. Real implementations are added phase by phase.
STAGES = ["script", "qa", "voice", "visuals", "render", "upload"]

MAX_ATTEMPTS = 3

StageFn = Callable[[sqlite3.Row], None]


def run_job(conn: sqlite3.Connection, job: sqlite3.Row, handlers: dict[str, StageFn]) -> None:
    start = 0 if job["stage"] == "new" else STAGES.index(job["stage"]) + 1
    for stage in STAGES[start:]:
        handler = handlers.get(stage)
        if handler is None:
            return  # stage not implemented yet; leave job where it is
        started = time.time()
        print(f"[job {job['id']}] {stage} ...", flush=True)
        try:
            handler(job)
        except Exception as exc:  # noqa: BLE001 - recorded, not swallowed
            print(f"[job {job['id']}] {stage} FAILED: {exc}", flush=True)
            conn.execute(
                "UPDATE jobs SET attempts = attempts + 1, error = ?, "
                "status = CASE WHEN attempts + 1 >= ? THEN 'failed' ELSE 'pending' END "
                "WHERE id = ?",
                (f"{stage}: {exc}", MAX_ATTEMPTS, job["id"]),
            )
            conn.commit()
            return
        print(f"[job {job['id']}] {stage} done in {time.time() - started:.0f}s", flush=True)
        conn.execute("UPDATE jobs SET stage = ?, error = NULL WHERE id = ?", (stage, job["id"]))
        conn.commit()
    conn.execute("UPDATE jobs SET status = 'done' WHERE id = ?", (job["id"],))
    conn.commit()


def run_pending(conn: sqlite3.Connection, handlers: dict[str, StageFn]) -> int:
    """Run every pending job, retrying a failed job within this run until it succeeds or hits the cap."""
    ids = [r["id"] for r in conn.execute("SELECT id FROM jobs WHERE status = 'pending' ORDER BY id")]
    for job_id in ids:
        for _ in range(MAX_ATTEMPTS):
            job = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
            if job["status"] != "pending":
                break
            run_job(conn, job, handlers)
    return len(ids)
