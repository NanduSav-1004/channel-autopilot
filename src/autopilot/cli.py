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


MAX_TOPIC_TRIES = 3        # a topic whose script keeps failing the fact-check is replaced, up to this many topics per run


def ensure_progress(before: int, after: int) -> None:
    """A daily run that finishes no video must fail loudly: a green no-op would hide a dead channel."""
    if after <= before:
        print("ERROR: daily run finished no video (see job errors below)", file=sys.stderr)
        sys.exit(1)


def discover_with_retries(conn, cfg, want: int, tries: int = 3, pause: float = 60.0, avoid: set[str] | None = None) -> list[int]:
    """A brief outage of the model providers or Wikipedia must not cost the day's video: wait and try again."""
    import time

    from autopilot.errors import TransientError

    for attempt in range(tries):
        try:
            ids = topics.discover_mix(conn, cfg.niche, want, active_mix(cfg), avoid=avoid, forbidden=cfg.forbidden_topics,
                                      min_source_chars=cfg.formats["long"]["min_source_chars"])
            if ids or attempt == tries - 1:
                return ids
            print(f"[topics] attempt {attempt + 1}/{tries}: every candidate was rejected; asking the model again", flush=True)
        except (TransientError, OSError) as exc:
            print(f"[topics] attempt {attempt + 1}/{tries} failed: {type(exc).__name__}: {exc}", flush=True)
            if attempt == tries - 1:
                raise
            time.sleep(pause * (attempt + 1))
    return []


def active_mix(cfg) -> dict:
    """The topic mix, only when switched on (topics.enabled); otherwise every topic is core, as before."""
    t = cfg.topics or {}
    return t.get("mix", {}) if t.get("enabled") else {}


def preview_topics(conn, cfg, n: int) -> None:
    """What the mix would pick for the next n videos, on a scratch copy of the job list: nothing is queued."""
    scratch = db.connect(":memory:")
    for r in conn.execute("SELECT topic, source_title, kind, category FROM jobs WHERE kind = 'long' ORDER BY id"):
        scratch.execute("INSERT INTO jobs (topic, source_title, kind, category) VALUES (?, ?, ?, ?)",
                        (r["topic"], r["source_title"], r["kind"], r["category"]))
    mix = (cfg.topics or {}).get("mix", {})
    for i in range(n):
        ids = topics.discover_mix(scratch, cfg.niche, 1, mix, forbidden=cfg.forbidden_topics,
                                  min_source_chars=cfg.formats["long"]["min_source_chars"])
        for row in scratch.execute("SELECT category, topic, source_title FROM jobs WHERE id = ?", (ids[0],)) if ids else []:
            print(f"PROPOSED {i + 1}: [{row['category']}] {row['topic']}  (source: {row['source_title']})", flush=True)
        if not ids:
            print(f"PROPOSED {i + 1}: nothing found this time", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(prog="autopilot")
    parser.add_argument("command", choices=["topics", "run", "daily", "status", "retry", "thumbnails", "ml"])
    parser.add_argument("--privacy", choices=["private", "unlisted", "public"], default="private")
    parser.add_argument("--live", action="store_true", help="really upload (overrides dry_run in config)")
    parser.add_argument("--force", action="store_true", help="make a video even if today's is already uploaded")
    parser.add_argument("--src", help="ml: the finished English job folder to make a Malayalam edition of")
    parser.add_argument("--auto", action="store_true", help="ml: make and upload today's Malayalam edition (after `daily`)")
    parser.add_argument("--preview", type=int, metavar="N", help="topics: show the next N proposed topics without queueing any")
    parser.add_argument("--redo-shorts", action="store_true", help="ml --auto: delete today's still-private Malayalam Shorts and rebuild them")
    parser.add_argument("--retry", action="store_true", help="ml --auto: also retry editions that failed earlier today")
    parser.add_argument("--voice", help="ml: Gemini voice name (default: rotates Charon, Achird, Sulafat)")
    args = parser.parse_args()

    load_env()
    cfg = load_config()
    if args.live:
        cfg.dry_run = False
    if args.command == "ml" and args.auto:
        from pathlib import Path

        from autopilot import malayalam

        if args.live:
            cfg.dry_run = False
        conn = db.connect()
        if args.redo_shorts:
            for line in malayalam.redo_shorts(conn):
                print(f"[ml] {line}", flush=True)
        print(malayalam.run_daily_edition(conn, cfg, args.privacy, not cfg.dry_run, Path("output"), args.retry or args.redo_shorts),
              flush=True)
        return
    if args.command == "ml":
        from pathlib import Path

        from autopilot import malayalam

        src = Path(args.src)
        voice = {"engine": "gemini", "name": args.voice} if args.voice else malayalam.pick_ml_voice(
            int(src.name.split("-")[0]))
        out = malayalam.build_edition(src, src / "ml", Path("work") / "ml" / src.name, voice)
        print(f"Malayalam edition: {out}")
        return
    if args.command == "topics" and args.preview:
        preview_topics(db.connect(), cfg, args.preview)
        return
    conn = db.connect()
    done_before = done_count(conn)
    skip_discovery = False
    if args.command == "daily" and not cfg.dry_run and not args.force and already_done_today(conn, cfg):
        stages = Stages(conn, cfg, privacy=args.privacy)
        added = stages.fill_missing_shorts()       # the daily rule is N Shorts: a run that finds fewer repairs the day
        pending = db.pending_count(conn, "long") + db.pending_count(conn, "short")
        if not added and not pending:
            print("today's video is already uploaded; nothing to do (use --force to make another)")
            return
        print(f"[daily] today's video is up; finishing its Shorts ({added} queued, {pending} already pending)", flush=True)
        skip_discovery = True
    if args.command in ("topics", "daily") and not skip_discovery:
        want = cfg.formats["long"]["per_day"] - db.pending_count(conn, "long")
        if want > 0:
            ids = discover_with_retries(conn, cfg, want)
            print(f"queued {len(ids)} new topic(s)")
    if args.command in ("run", "daily"):
        tries = MAX_TOPIC_TRIES if args.command == "daily" else 1
        for round_ in range(tries):
            n = run_pending(conn, Stages(conn, cfg, privacy=args.privacy).handlers())
            print(f"processed {n} job(s); dry_run={cfg.dry_run}")
            if args.command != "daily" or done_count(conn) > done_before or round_ == tries - 1:
                break
            failed = [r["category"] or "core" for r in conn.execute(
                "SELECT category FROM jobs WHERE kind = 'long' AND status = 'failed' AND date(created_at) = date('now')")]
            if not failed:                    # nothing failed for good (an outage, say): a later run picks the same job up again
                break
            print(f"[daily] today's topic failed after all attempts ({', '.join(failed)}); choosing another topic", flush=True)
            discover_with_retries(conn, cfg, 1, avoid=set(failed))
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
