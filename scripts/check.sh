#!/usr/bin/env bash
# The checks GitHub CI used to run, now run locally: lint, tests, secret scan. Also the pre-push hook.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
echo "== lint";    .venv/bin/ruff check .
echo "== tests";   .venv/bin/pytest -q
echo "== secrets"; .venv/bin/python scripts/secret_scan.py
echo "all checks passed"
