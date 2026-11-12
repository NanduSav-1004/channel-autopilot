"""Facts about the running GitHub workflow for the failure alerts: which step failed (the old alert only had the last log lines, which for an
install failure were from an unrelated step)."""
import json
import os
import urllib.request


def failed_steps() -> str:
    """Names of the failed steps of this run, or '' if they cannot be read. Never raises."""
    try:
        repo, run, token = os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_RUN_ID"], os.environ["GITHUB_TOKEN"]
        req = urllib.request.Request(f"https://api.github.com/repos/{repo}/actions/runs/{run}/jobs",
                                     headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "User-Agent": "channel-autopilot"})
        with urllib.request.urlopen(req, timeout=20) as r:
            jobs = json.load(r).get("jobs", [])
        names = [s["name"] for j in jobs for s in j.get("steps", []) if s.get("conclusion") == "failure"]
        return ", ".join(names)
    except Exception:  # noqa: BLE001
        return ""
