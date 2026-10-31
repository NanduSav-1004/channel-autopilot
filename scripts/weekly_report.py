"""Weekly numbers for the three channels from the YouTube Analytics API (read-only). Usage: python scripts/weekly_report.py [--json out.json]"""
import json
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from googleapiclient.discovery import build

from autopilot import env
from autopilot.youtube_auth import load_credentials

CHANNELS = {"en": "Brightwork Science", "ml": "Brightwork Malayalam", "data": "Plotline Data"}
METRICS = "views,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost,likes,comments,shares"


def rows(resp: dict) -> list[dict]:
    names = [h["name"] for h in resp.get("columnHeaders", [])]
    return [dict(zip(names, r, strict=True)) for r in resp.get("rows", [])]


def q(an, start: date, end: date, metrics: str = METRICS, **kw) -> list[dict]:
    try:
        return rows(an.reports().query(ids="channel==MINE", startDate=str(start), endDate=str(end), metrics=metrics, **kw).execute())
    except Exception as exc:  # noqa: BLE001
        return [{"error": str(exc)[:160]}]


def main() -> None:
    env.load_env(ROOT / ".env")
    end = date.today() - timedelta(days=2)           # the newest two days are still incomplete in Analytics
    out = {"end": str(end)}
    for prof in CHANNELS:
        creds = load_credentials(prof)
        yt, an = build("youtube", "v3", credentials=creds), build("youtubeAnalytics", "v2", credentials=creds)
        ch = yt.channels().list(part="snippet,statistics", mine=True).execute()["items"][0]
        info = {"title": ch["snippet"]["title"], "created": ch["snippet"]["publishedAt"][:10], "stats": ch["statistics"]}
        w1s = end - timedelta(days=6)
        w0e, w0s = w1s - timedelta(days=1), w1s - timedelta(days=7)
        life_start = date.fromisoformat(info["created"])
        info["last7"] = q(an, w1s, end)
        info["prev7"] = q(an, w0s, w0e)
        info["lifetime"] = q(an, life_start, end)
        info["last365"] = q(an, end - timedelta(days=364), end, "views,estimatedMinutesWatched")
        info["daily"] = q(an, max(life_start, end - timedelta(days=13)), end, "views,estimatedMinutesWatched,subscribersGained", dimensions="day", sort="day")
        info["by_type"] = q(an, life_start, end, "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage", dimensions="creatorContentType")
        info["countries"] = q(an, life_start, end, "views,estimatedMinutesWatched", dimensions="country", sort="-views", maxResults=8)
        info["traffic"] = q(an, life_start, end, "views,estimatedMinutesWatched", dimensions="insightTrafficSourceType", sort="-views", maxResults=8)
        info["videos"] = q(an, life_start, end, "views,estimatedMinutesWatched,averageViewPercentage,subscribersGained,likes", dimensions="video", sort="-views", maxResults=60)
        ids = [v["video"] for v in info["videos"] if "video" in v][:50]
        if ids:
            meta = yt.videos().list(part="snippet,contentDetails", id=",".join(ids)).execute()["items"]
            info["titles"] = {m["id"]: {"title": m["snippet"]["title"], "published": m["snippet"]["publishedAt"][:16], "dur": m["contentDetails"]["duration"]} for m in meta}
        out[prof] = info
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps(out, indent=1))
    else:
        print(json.dumps(out, indent=1)[:6000])


if __name__ == "__main__":
    main()
