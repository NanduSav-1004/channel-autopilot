import argparse
import sys

from autopilot import db, notify, topics
from autopilot.config import load_config
from autopilot.env import load_env
from autopilot.pipeline import run_pending
from autopilot.stages import Stages


def done_count(conn) -> int:
    return conn.execute("SELECT COUNT(*) FROM jobs WHERE status = 'done'").fetchone()[0]


def already_done_today(conn, cfg) -> bool:
    """Redundant schedule times and manual runs must not stack up several videos in one day."""
    return db.uploaded_today(conn, "long") >= cfg.formats["long"]["per_day"]


def notify_uploaded(conn) -> None:
    row = conn.execute("SELECT video_id, topic, publish_at FROM jobs WHERE kind = 'long' AND video_id IS NOT NULL "
                       "ORDER BY id DESC LIMIT 1").fetchone()
    shorts = conn.execute("SELECT COUNT(*) FROM jobs WHERE kind = 'short' AND video_id IS NOT NULL "
                          "AND date(created_at) = date('now')").fetchone()[0]
    if row:
        notify.send(f"Brightwork: uploaded {row['topic']!r}\nhttps://youtu.be/{row['video_id']}\n"
                    f"goes public {row['publish_at'] or 'now'} UTC; {shorts} Short(s) queued")


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
    parser.add_argument("--force", action="store_true", help="make a video even if today's is already uploaded")
    args = parser.parse_args()

    load_env()
    cfg = load_config()
    if args.live:
        cfg.dry_run = False
    conn = db.connect()
    done_before = done_count(conn)
    if args.command == "daily" and not cfg.dry_run and not args.force and already_done_today(conn, cfg):
        print("today's video is already uploaded; nothing to do (use --force to make another)")
        return
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
