"""Stage runner: each stage is idempotent; failures are recorded and never block the queue."""
import sqlite3
import time
from collections.abc import Callable

from autopilot.errors import RestartJob, TransientError

# Ordered stages per job kind. Stage names are unique across kinds so one flat handler dict serves both.
# A long job ends by planning its Shorts, which are queued as separate jobs.
STAGES = ["script", "qa", "voice", "visuals", "render", "upload", "shorts"]
SHORT_STAGES = ["short_script", "short_voice", "short_render", "short_upload"]
STAGE_SETS = {"long": STAGES, "short": SHORT_STAGES}

MAX_ATTEMPTS = 3

StageFn = Callable[[sqlite3.Row], None]


def run_job(
    conn: sqlite3.Connection, job: sqlite3.Row, handlers: dict[str, StageFn], _restarted: bool = False,
) -> str:
    """Returns 'done', 'stalled' (no handler yet), 'failed' (attempt recorded) or 'transient'."""
    stages = STAGE_SETS[job["kind"]]
    start = 0 if job["stage"] == "new" else stages.index(job["stage"]) + 1
    for stage in stages[start:]:
        handler = handlers.get(stage)
        if handler is None:
            return "stalled"  # stage not implemented yet; leave job where it is
        started = time.time()
        print(f"[job {job['id']}] {stage} ...", flush=True)
        try:
            handler(job)
        except Exception as exc:  # noqa: BLE001 - recorded, not swallowed
            if isinstance(exc, RestartJob) and not _restarted:
                print(f"[job {job['id']}] {stage}: {exc}; rewinding to the start", flush=True)
                conn.execute("UPDATE jobs SET stage = 'new' WHERE id = ?", (job["id"],))
                conn.commit()
                fresh = conn.execute("SELECT * FROM jobs WHERE id = ?", (job["id"],)).fetchone()
                return run_job(conn, fresh, handlers, _restarted=True)
            print(f"[job {job['id']}] {stage} FAILED: {exc}", flush=True)
            if isinstance(exc, TransientError):
                conn.execute("UPDATE jobs SET error = ? WHERE id = ?", (f"{stage}: {exc} (will retry)", job["id"]))
                conn.commit()
                return "transient"
            conn.execute(
                "UPDATE jobs SET attempts = attempts + 1, error = ?, "
                "status = CASE WHEN attempts + 1 >= ? THEN 'failed' ELSE 'pending' END "
                "WHERE id = ?",
                (f"{stage}: {exc}", MAX_ATTEMPTS, job["id"]),
            )
            conn.commit()
            return "failed"
        print(f"[job {job['id']}] {stage} done in {time.time() - started:.0f}s", flush=True)
        conn.execute("UPDATE jobs SET stage = ?, error = NULL WHERE id = ?", (stage, job["id"]))
        conn.commit()
    conn.execute("UPDATE jobs SET status = 'done' WHERE id = ?", (job["id"],))
    conn.commit()
    return "done"


def run_pending(conn: sqlite3.Connection, handlers: dict[str, StageFn]) -> int:
    """Run every pending job, retrying a failed job within this run until it succeeds or hits the cap.
    Jobs queued while running (a long video's Shorts) are picked up in the same run."""
    seen: set[int] = set()
    while True:
        ids = [r["id"] for r in conn.execute("SELECT id FROM jobs WHERE status = 'pending' ORDER BY id")
               if r["id"] not in seen]
        if not ids:
            return len(seen)
        for job_id in ids:
            seen.add(job_id)
            for _ in range(MAX_ATTEMPTS):
                job = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
                if job["status"] != "pending":
                    break
                if run_job(conn, job, handlers) in ("transient", "stalled", "done"):
                    break  # transient: retry on a later run; the others need no further passes
