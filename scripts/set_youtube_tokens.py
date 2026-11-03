"""Copy the three channels' YouTube refresh tokens from secrets/ into GitHub Actions secrets with the gh CLI (values are piped, never printed).

usage: python scripts/set_youtube_tokens.py [owner/repo]     (needs `gh auth login` first)
Run it after renewing the logins (python -m autopilot.youtube_auth [--ml|--data]); the new tokens also carry the comment permission.
"""
import json
import subprocess
import sys

repo = sys.argv[1] if len(sys.argv) > 1 else "NanduSav-1004/channel-autopilot"
for name, path in (("YOUTUBE_REFRESH_TOKEN", "secrets/token.json"), ("YOUTUBE_REFRESH_TOKEN_ML", "secrets/token_ml.json"),
                   ("YOUTUBE_REFRESH_TOKEN_DATA", "secrets/token_data.json")):
    token = json.load(open(path))["refresh_token"]
    result = subprocess.run(["gh", "secret", "set", name, "--repo", repo], input=token.encode(), capture_output=True, check=False)
    print(f"{name}: " + ("set" if result.returncode == 0 else "FAILED " + result.stderr.decode()[:200]))
