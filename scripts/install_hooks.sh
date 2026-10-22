#!/usr/bin/env bash
git config core.hooksPath .githooks && echo "pre-push hook installed (runs scripts/check.sh before every push)"
