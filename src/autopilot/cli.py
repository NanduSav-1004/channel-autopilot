import argparse

from autopilot import db
from autopilot.config import load_config
from autopilot.pipeline import run_pending


def main() -> None:
    parser = argparse.ArgumentParser(prog="autopilot")
    parser.add_argument("command", choices=["run", "status"])
    args = parser.parse_args()

    cfg = load_config()
    conn = db.connect()
    if args.command == "run":
        n = run_pending(conn, handlers={})  # handlers registered as stages are built
        print(f"processed {n} pending job(s); dry_run={cfg.dry_run}")
    else:
        for row in conn.execute("SELECT id, kind, stage, status, topic FROM jobs"):
            print(dict(row))


if __name__ == "__main__":
    main()
