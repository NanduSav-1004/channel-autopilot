#!/usr/bin/env bash
# Keeps the Science Chaya ledger (data/chaya_state.json) on a single-commit `state-chaya` branch.
# usage: scripts/chaya_state.sh pull|push   (needs GITHUB_TOKEN and GITHUB_REPOSITORY; STATE_REMOTE overrides the URL)
set -euo pipefail
REMOTE="${STATE_REMOTE:-https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git}"
F=data/chaya_state.json
case "${1:-}" in
  pull)
    mkdir -p data
    if git ls-remote --exit-code --heads "$REMOTE" state-chaya >/dev/null 2>&1; then
      git fetch --quiet --depth=1 "$REMOTE" state-chaya
      git show "FETCH_HEAD:$F" > "$F"
    else
      echo '{"offset": null, "items": {}}' > "$F"
    fi
    ;;
  push)
    tmp="$(mktemp -d)"; cp "$F" "$tmp/chaya_state.json"
    git -C "$tmp" init -q -b state-chaya
    mkdir -p "$tmp/data"; mv "$tmp/chaya_state.json" "$tmp/$F"
    git -C "$tmp" -c user.name=autopilot -c user.email=autopilot@users.noreply.github.com add -A
    git -C "$tmp" -c user.name=autopilot -c user.email=autopilot@users.noreply.github.com commit -q -m "chaya state"
    for wait in 0 8 25; do
      sleep "$wait"
      if git -C "$tmp" push -q -f "$REMOTE" state-chaya 2>/dev/null; then exit 0; fi
    done
    echo "chaya state push failed" >&2; exit 1
    ;;
  *) echo "usage: $0 pull|push" >&2; exit 2 ;;
esac
