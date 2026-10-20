import argparse
import sys

from autopilot import db, topics
from autopilot.config import load_config
from autopilot.env import load_env
from autopilot.pipeline import run_pending
from autopilot.stages import Stages


def done_count(conn) -> int:
    return conn.execute("SELECT COUNT(*) FROM jobs WHERE status = 'done'").fetchone()[0]


def ensure_progress(before: int, after: int) -> None:
    """A daily run that finishes no video must fail loudly: a green no-op would hide a dead channel."""
    if after <= before:
        print("ERROR: daily run finished no video (see job errors below)", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(prog="autopilot")
    parser.add_argument("command", choices=["topics", "run", "daily", "status", "retry", "thumbnails"])
    parser.add_argument("--privacy", choices=["private", "unlisted", "public"], default="private")
    parser.add_argument("--live", action="store_true", help="really upload (overrides dry_run in config)")
    args = parser.parse_args()

    load_env()
    cfg = load_config()
    if args.live:
        cfg.dry_run = False
    conn = db.connect()
    done_before = done_count(conn)
    if args.command in ("topics", "daily"):
        want = cfg.formats["long"]["per_day"] - db.pending_count(conn, "long")
        if want > 0:
            ids = topics.discover(conn, cfg.niche, want, forbidden=cfg.forbidden_topics,
                                  min_source_chars=cfg.formats["long"]["min_source_chars"])
            print(f"queued {len(ids)} new topic(s)")
    if args.command in ("run", "daily"):
        n = run_pending(conn, Stages(conn, cfg, privacy=args.privacy).handlers())
        print(f"processed {n} job(s); dry_run={cfg.dry_run}")
        if args.command == "daily":
            for row in conn.execute("SELECT id, stage, status, attempts, error FROM jobs WHERE status != 'done'"):
                print(dict(row))
            ensure_progress(done_before, done_count(conn))
    if args.command == "retry":
        n = conn.execute(
            "UPDATE jobs SET status = 'pending', attempts = 0, error = NULL WHERE status = 'failed'"
        ).rowcount
        conn.commit()
        print(f"reset {n} failed job(s)")
    if args.command == "thumbnails":
        st = Stages(conn, cfg)
        rows = conn.execute("SELECT * FROM jobs WHERE video_id IS NOT NULL AND thumbnail_set = 0").fetchall()
        ok = sum(st.set_thumbnail(r["id"], r["video_id"], st.dir(r) / "thumbnail.jpg") for r in rows)
        print(f"thumbnails set for {ok}/{len(rows)} video(s)")
    if args.command == "status":
        for row in conn.execute("SELECT id, kind, stage, status, attempts, video_id, topic, error FROM jobs"):
            print(dict(row))


if __name__ == "__main__":
    main()
