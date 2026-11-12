#!/usr/bin/env bash
# Fonts and ffmpeg for the workflows. apt on the hosted runners fails now and then (a mirror that does not answer: on 11 Nov 2026 two runs lost 40
# minutes and then failed here), so: short timeouts, three attempts, and a clear message. Usage: scripts/install_system_packages.sh [packages...]
set -u
PKGS="${*:-fonts-lato fonts-dejavu-core fonts-noto-core ffmpeg}"          # default: everything Brightwork needs; Plotline passes a shorter list
OPTS="-o Acquire::Retries=3 -o Acquire::http::Timeout=30 -o Acquire::https::Timeout=30"
for attempt in 1 2 3; do
  if sudo timeout 120 apt-get $OPTS update -qq && \
     sudo timeout 300 apt-get $OPTS install -y -qq $PKGS; then
    echo "system packages installed (attempt $attempt)"
    exit 0
  fi
  echo "apt attempt $attempt failed; waiting before the next one" >&2
  sleep $((attempt * 20))
done
echo "system packages could NOT be installed after 3 attempts" >&2
exit 1
