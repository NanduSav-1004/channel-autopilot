"""Lightweight local secret scan: key-shaped strings anywhere in the repo's history, and files that must never be tracked.

Runs in the pre-push hook. It is narrower than gitleaks (it only knows the key shapes this project uses, plus common
ones), so the full gitleaks scan stays available as a manual GitHub workflow.
"""
import re
import subprocess
import sys

PATTERNS = {
    "Google API key": r"AIza[0-9A-Za-z_-]{35}",
    "Groq API key": r"gsk_[0-9A-Za-z]{40,}",
    "Google OAuth client secret": r"GOCSPX-[0-9A-Za-z_-]{20,}",
    "Google access token": r"ya29\.[0-9A-Za-z_-]{30,}",
    "Google refresh token": r"1//0[0-9A-Za-z_-]{40,}",
    "GitHub token": r"gh[pousr]_[0-9A-Za-z]{36,}|github_pat_[0-9A-Za-z_]{40,}",
    "AWS access key": r"AKIA[0-9A-Z]{16}",
    "Private key block": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "Slack token": r"xox[baprs]-[0-9A-Za-z-]{20,}",
}
NEVER_TRACKED = re.compile(r"(^|/)(\.env(\..*)?|token[^/]*\.json|client_secret[^/]*\.json|credentials[^/]*\.json)$|(^|/)secrets/")
ALLOWED = {".env.example"}


def find_secrets(text: str) -> list[tuple[str, str]]:
    return [(name, m.group(0)) for name, rx in PATTERNS.items() for m in re.finditer(rx, text)]


def forbidden_files(paths: list[str]) -> list[str]:
    return [p for p in paths if NEVER_TRACKED.search(p) and p.rsplit("/", 1)[-1] not in ALLOWED]


def main() -> int:
    problems = []
    tracked = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True).stdout.split("\n")
    problems += [f"tracked file that must never be committed: {p}" for p in forbidden_files([p for p in tracked if p])]
    history = subprocess.run(["git", "log", "-p", "--all", "--no-color"], capture_output=True, text=True, check=True).stdout
    for name, hit in sorted(set(find_secrets(history))):
        problems.append(f"{name} in git history: {hit[:6]}...{hit[-3:]}")
    for p in problems:
        print("SECRET SCAN:", p)
    print("secret scan:", "FAILED" if problems else "clean")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
