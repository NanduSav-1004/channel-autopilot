import argparse

from autopilot import db, topics
from autopilot.config import load_config
from autopilot.env import load_env
from autopilot.pipeline import run_pending
from autopilot.stages import Stages


def main() -> None:
    parser = argparse.ArgumentParser(prog="autopilot")
    parser.add_argument("command", choices=["topics", "run", "daily", "status"])
    parser.add_argument("--privacy", choices=["private", "unlisted", "public"], default="private")
    parser.add_argument("--live", action="store_true", help="really upload (overrides dry_run in config)")
    args = parser.parse_args()

    load_env()
    cfg = load_config()
    if args.live:
        cfg.dry_run = False
    conn = db.connect()
    if args.command in ("topics", "daily"):
        want = cfg.formats["long"]["per_day"] - db.pending_count(conn, "long")
        if want > 0:
            ids = topics.discover(conn, cfg.niche, want, forbidden=cfg.forbidden_topics)
            print(f"queued {len(ids)} new topic(s)")
    if args.command in ("run", "daily"):
        n = run_pending(conn, Stages(conn, cfg, privacy=args.privacy).handlers())
        print(f"processed {n} job(s); dry_run={cfg.dry_run}")
    if args.command == "status":
        for row in conn.execute("SELECT id, kind, stage, status, attempts, video_id, topic, error FROM jobs"):
            print(dict(row))


if __name__ == "__main__":
    main()
