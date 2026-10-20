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
      echo "state restored"
    else
      echo "no state branch yet: starting fresh"
    fi
    ;;
  push)
    [ -f "$DB" ] || { echo "no database to save"; exit 0; }
    tmp="$(mktemp -d)"
    mkdir "$tmp/data" && cp "$DB" "$tmp/$DB"
    cd "$tmp"
    git init -q -b state
    git add "$DB"
    git -c user.name=autopilot-bot -c user.email=autopilot-bot@users.noreply.github.com \
        commit -q -m "state $(date -u +%FT%TZ)"
    git push --quiet --force "$REMOTE" state
    echo "state saved"
    ;;
  *) echo "usage: $0 pull|push" >&2; exit 2 ;;
esac
