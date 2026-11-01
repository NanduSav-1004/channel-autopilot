"""Hourly job: post each new public video's first comment (the channel's own comment question) and send new viewer comments to Telegram.
Reads the video maps from the `state` and `state-plotline` branches, keeps its own ledger on the `state-comments` branch.
Usage: python scripts/comments_run.py [--dry-run]   (needs the YouTube secrets and, to save the ledger, GITHUB_TOKEN + GITHUB_REPOSITORY)"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from googleapiclient.discovery import build

from autopilot import comments, env, notify
from autopilot.youtube_auth import configured, load_credentials

CHANNELS = {"en": ("Brightwork Science", "origin/state", "data/video_maps"),
            "data": ("Plotline Data", "origin/state-plotline", "data/plotline/video_maps"),
            "ml": ("Brightwork Malayalam", None, None)}                 # Malayalam: only viewer-comment alerts for now


def git(*args: str, cwd: Path = ROOT) -> str | None:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)
    return r.stdout if r.returncode == 0 else None


def remote() -> str | None:
    tok, repo = os.environ.get("GITHUB_TOKEN"), os.environ.get("GITHUB_REPOSITORY")
    return f"https://x-access-token:{tok}@github.com/{repo}.git" if tok and repo else None


def fetch() -> None:
    url = remote()
    for branch in ("state", "state-plotline", "state-comments"):
        git("fetch", "--quiet", "--depth=1", url or "origin", f"{branch}:refs/remotes/origin/{branch}")


def load_maps(ref: str, folder: str) -> dict:
    out = {}
    for path in (git("ls-tree", "-r", "--name-only", ref, folder) or "").split():
        text = git("show", f"{ref}:{path}")
        if text:
            m = json.loads(text)
            out[m.get("video_id") or Path(path).stem] = m
    return out


def load_ledger() -> dict:
    text = git("show", "origin/state-comments:data/comments/ledger.json")
    return {**comments.empty_ledger(), **(json.loads(text) if text else {})}


def save_ledger(ledger: dict) -> None:
    url = remote()
    if not url:
        print("[comments] no GITHUB_TOKEN: ledger not saved")
        return
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        (d / "data" / "comments").mkdir(parents=True)
        (d / "data" / "comments" / "ledger.json").write_text(comments.dumps(ledger))
        for cmd in (["init", "-q", "-b", "state-comments"], ["add", "-A"],
                    ["-c", "user.name=autopilot", "-c", "user.email=autopilot@users.noreply.github.com", "commit", "-q", "-m", "comments ledger"],
                    ["push", "-q", "-f", url, "state-comments"]):
            if git(*cmd, cwd=d) is None:
                print(f"[comments] ledger save failed at: git {cmd[0]}")
                return
    print("[comments] ledger saved")


def main() -> None:
    env.load_env(ROOT / ".env")
    dry = "--dry-run" in sys.argv
    fetch()
    ledger = load_ledger()
    send = (lambda t: print("[dry-run] would send:", t)) if dry else notify.send
    yts: dict = {}
    for prof, (name, ref, folder) in CHANNELS.items():
        if not configured(prof):
            print(f"[comments] {name}: no login, skipped")
            continue
        yt = yts[prof] = build("youtube", "v3", credentials=load_credentials(prof))
        maps = load_maps(ref, folder) if ref else {}
        try:
            if dry:
                print(f"[dry-run] {name}: {len(comments.due(maps, ledger))} first comments waiting")
                continue
            comments.run_profile(yt, prof, name, maps, ledger, send)
        except Exception as exc:  # noqa: BLE001 - one channel's problem must not stop the others
            print(f"[comments] {name}: {type(exc).__name__}: {str(exc)[:200]}")
    if not dry:
        try:                                                              # the owner's answers to the draft replies (ok N, skip N, N: own words)
            comments.process_approvals(notify.updates(ledger.get("tg_offset")), ledger, yts, os.environ.get("TELEGRAM_CHAT_ID", ""), send)
            comments.expire_pending(ledger)
        except Exception as exc:  # noqa: BLE001
            print(f"[comments] approvals: {type(exc).__name__}: {str(exc)[:200]}")
        save_ledger(ledger)


if __name__ == "__main__":
    main()
