#!/usr/bin/env bash
# Keeps the job database between scheduled runs on a single-commit `state` branch.
# usage: scripts/state_sync.sh pull|push   (needs GITHUB_TOKEN and GITHUB_REPOSITORY)
set -euo pipefail
# STATE_REMOTE overrides the GitHub URL (used by tests)
REMOTE="${STATE_REMOTE:-https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git}"
DB=data/autopilot.db

case "${1:-}" in
  pull)
    mkdir -p data
    if git ls-remote --exit-code --heads "$REMOTE" state >/dev/null 2>&1; then
      git fetch --quiet --depth=1 "$REMOTE" state
      git show "FETCH_HEAD:$DB" > "$DB"
      git show "FETCH_HEAD:data/last_work_run.log" > data/last_work_run.log 2>/dev/null || rm -f data/last_work_run.log
      echo "state restored"
    else
      echo "no state branch yet: starting fresh"
    fi
    ;;
  push)
    [ -f "$DB" ] || { echo "no database to save"; exit 0; }
    tmp="$(mktemp -d)"
    mkdir "$tmp/data" && cp "$DB" "$tmp/$DB"
    if [ -f run.log ]; then  # last 400 lines, with anything that looks like a key masked
      tail -n 400 run.log | sed -E 's/(AIza[0-9A-Za-z_-]{20,}|gsk_[0-9A-Za-z]{16,}|GOCSPX-[0-9A-Za-z_-]{8,}|ya29\.[0-9A-Za-z_-]{20,}|1\/\/[0-9A-Za-z_-]{20,})/***/g' > "$tmp/data/last_run.log"
    fi
    # A run that only found "nothing to do" must not hide the log of the run that actually made the video.
    if [ -f run.log ] && ! grep -q "nothing to do" run.log; then
      cp "$tmp/data/last_run.log" "$tmp/data/last_work_run.log" 2>/dev/null || true
    elif [ -f data/last_work_run.log ]; then
      cp data/last_work_run.log "$tmp/data/last_work_run.log"
    fi
    cd "$tmp"
    git init -q -b state
    git add data
    git -c user.name=autopilot-bot -c user.email=autopilot-bot@users.noreply.github.com \
        commit -q -m "state $(date -u +%FT%TZ)"
    git push --quiet --force "$REMOTE" state
    echo "state saved"
    ;;
  *) echo "usage: $0 pull|push" >&2; exit 2 ;;
esac
