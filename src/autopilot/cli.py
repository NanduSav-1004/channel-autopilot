import argparse
import sys
from datetime import timedelta, timezone

from autopilot import db, notify, schedule, topics
from autopilot.config import load_config
from autopilot.env import load_env
from autopilot.pipeline import run_pending
from autopilot.stages import Stages


def done_count(conn) -> int:
    return conn.execute("SELECT COUNT(*) FROM jobs WHERE status = 'done'").fetchone()[0]


def already_done_today(conn, cfg) -> bool:
    """Redundant schedule times and manual runs must not stack up several videos in one day."""
    return db.uploaded_today(conn, "long") >= cfg.formats["long"]["per_day"]


def ist(ts: str | None) -> str:
    """'2026-10-24T18:00:00Z' -> '24 Oct 11:30 PM IST (18:00 UTC)'; the owner works in Indian time."""
    if not ts:
        return "immediately"
    dt = schedule.parse(ts)
    local = dt.astimezone(timezone(timedelta(hours=5, minutes=30)))
    return f"{local:%d %b} {local.strftime('%I:%M %p').lstrip('0')} IST ({dt:%H:%M} UTC)"


def notify_uploaded(conn) -> None:
    row = conn.execute("SELECT id, video_id, topic, publish_at FROM jobs WHERE kind = 'long' AND video_id IS NOT NULL "
                       "ORDER BY id DESC LIMIT 1").fetchone()
    if not row:
        return
    shorts = conn.execute("SELECT publish_at FROM jobs WHERE kind = 'short' AND parent_id = ? AND video_id IS NOT NULL "
                          "ORDER BY publish_at", (row["id"],)).fetchall()
    lines = [f"Brightwork: uploaded {row['topic']!r}", f"https://youtu.be/{row['video_id']}",
             f"Goes public: {ist(row['publish_at'])}"]
    lines += [f"Short {i}: {ist(s['publish_at'])}" for i, s in enumerate(shorts, 1)] or ["No Shorts queued"]
    notify.send("\n".join(lines))


def ensure_progress(before: int, after: int) -> None:
    """A daily run that finishes no video must fail loudly: a green no-op would hide a dead channel."""
    if after <= before:
        print("ERROR: daily run finished no video (see job errors below)", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(prog="autopilot")
    parser.add_argument("command", choices=["topics", "run", "daily", "status", "retry", "thumbnails", "ml"])
    parser.add_argument("--privacy", choices=["private", "unlisted", "public"], default="private")
    parser.add_argument("--live", action="store_true", help="really upload (overrides dry_run in config)")
    parser.add_argument("--force", action="store_true", help="make a video even if today's is already uploaded")
    parser.add_argument("--src", help="ml: the finished English job folder to make a Malayalam edition of")
    parser.add_argument("--voice", help="ml: Gemini voice name (default: rotates Charon, Achird, Sulafat)")
    args = parser.parse_args()

    load_env()
    cfg = load_config()
    if args.live:
        cfg.dry_run = False
    if args.command == "ml":
        from pathlib import Path

        from autopilot import malayalam

        src = Path(args.src)
        voice = {"engine": "gemini", "name": args.voice} if args.voice else malayalam.pick_ml_voice(
            int(src.name.split("-")[0]))
        out = malayalam.build_edition(src, src / "ml", Path("work") / "ml" / src.name, voice)
        print(f"Malayalam edition: {out}")
        return
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
