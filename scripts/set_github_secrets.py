"""Copy local credentials into GitHub Actions secrets with the gh CLI. Values are piped, never printed.

usage: python scripts/set_github_secrets.py [owner/repo]
Reads .env (GEMINI/GROQ/PIXABAY keys), client_secret.json and secrets/token.json.
"""
import json
import subprocess
import sys
from pathlib import Path

repo = sys.argv[1] if len(sys.argv) > 1 else "NanduSav-1004/channel-autopilot"


def env_values() -> dict:
    out = {}
    for line in Path(".env").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


env = env_values()
client = json.loads(Path("client_secret.json").read_text())["installed"]
token = json.loads(Path("secrets/token.json").read_text())
secrets = {
    "GEMINI_API_KEY": env.get("GEMINI_API_KEY", ""),
    "GROQ_API_KEY": env.get("GROQ_API_KEY", ""),
    "PIXABAY_API_KEY": env.get("PIXABAY_API_KEY", ""),
    "YOUTUBE_CLIENT_ID": client["client_id"],
    "YOUTUBE_CLIENT_SECRET": client["client_secret"],
    "YOUTUBE_REFRESH_TOKEN": token["refresh_token"],
}
for name, value in secrets.items():
    if not value:
        print(f"SKIP {name}: empty")
        continue
    subprocess.run(["gh", "secret", "set", name, "--repo", repo], input=value.encode(), check=True)
    print(f"set {name}")
