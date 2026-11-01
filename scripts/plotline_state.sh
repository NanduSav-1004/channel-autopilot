#!/usr/bin/env bash
# Keeps Plotline Data's state (data/plotline: state.json, and each day's plan, script and Shorts scripts) between runs on a
# single-commit `state-plotline` branch, separate from the Brightwork job database.
# usage: scripts/plotline_state.sh pull|push   (needs GITHUB_TOKEN and GITHUB_REPOSITORY)
set -euo pipefail
REMOTE="${STATE_REMOTE:-https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git}"
BRANCH=state-plotline
DIR=data/plotline

case "${1:-}" in
  pull)
    mkdir -p "$DIR"
    if git ls-remote --exit-code --heads "$REMOTE" "$BRANCH" >/dev/null 2>&1; then
      git fetch --quiet --depth=1 "$REMOTE" "$BRANCH"
      git ls-tree -r --name-only FETCH_HEAD | while read -r f; do
        mkdir -p "$(dirname "$f")"
        git show "FETCH_HEAD:$f" > "$f"
      done
      echo "plotline state restored"
    else
      echo "no plotline state yet: starting fresh"
    fi
    ;;
  push)
    [ -d "$DIR" ] || { echo "no plotline state to save"; exit 0; }
    tmp="$(mktemp -d)"
    mkdir -p "$tmp/data"
    # keep the last 60 days only
    cp -r "$DIR" "$tmp/data/"
    [ -f data/plotline_last_work_run.log ] && cp data/plotline_last_work_run.log "$tmp/data/"
    { ls -d "$tmp/$DIR"/20* 2>/dev/null || true; } | sort | head -n -60 | xargs -r rm -rf     # no dated folders yet is fine
    if [ -f plotline_run.log ]; then
      tail -n 400 plotline_run.log | sed -E 's/(AIza[0-9A-Za-z_-]{20,}|AQ\.[0-9A-Za-z_-]{20,}|gsk_[0-9A-Za-z]{16,}|GOCSPX-[0-9A-Za-z_-]{8,}|ya29\.[0-9A-Za-z_-]{20,}|1\/\/[0-9A-Za-z_-]{20,})/***/g' > "$tmp/data/plotline_last_run.log"
      # a run that only found "nothing to do" must not hide the log of the run that made the video (the same rule as Brightwork's state)
      grep -q "nothing to do" plotline_run.log || cp "$tmp/data/plotline_last_run.log" "$tmp/data/plotline_last_work_run.log"
    fi
    cd "$tmp"
    git init -q && git checkout -q -b "$BRANCH"
    git -c user.name=autopilot -c user.email=autopilot@users.noreply.github.com add -A
    git -c user.name=autopilot -c user.email=autopilot@users.noreply.github.com commit -q -m "plotline state $(date -u +%FT%TZ)"
    git push -q -f "$REMOTE" "$BRANCH"
    echo "plotline state saved"
    ;;
  *) echo "usage: $0 pull|push"; exit 2 ;;
esac
