"""Where do viewers leave? For each recent video with enough views: the hook leak, the steepest drop-offs and the replayed moments from the
YouTube Analytics retention curve (read-only), each mapped to the scene or section playing then.
Usage: python scripts/retention_report.py [--profile en|ml|data] [--min-views 20] [--days 28] [--json out.json]
The video maps come from data/video_maps/ (written at upload and kept on the state branches); for older Plotline videos the scenes are
estimated from the saved script. Without a map the report still gives the times."""
import json
import re
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from googleapiclient.discovery import build

from autopilot import env, retention
from autopilot.youtube_auth import load_credentials

CHANNELS = {"en": "Brightwork Science", "ml": "Brightwork Malayalam", "data": "Plotline Data"}


def iso_seconds(d: str) -> float:
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d)
    h, mi, s = (int(x or 0) for x in m.groups()) if m else (0, 0, 0)
    return h * 3600 + mi * 60 + s


def git_show(ref: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT, capture_output=True, text=True, check=False)
    return r.stdout if r.returncode == 0 else None


def load_map(profile: str, vid: str, title: str, duration: float) -> dict | None:
    """The saved map of a video, or (Plotline, older videos) one estimated from the day's saved script."""
    local = ROOT / ("data/plotline/video_maps" if profile == "data" else "data/video_maps") / f"{vid}.json"
    if local.exists():
        return json.loads(local.read_text())
    branch, path = ("origin/state-plotline", f"data/plotline/video_maps/{vid}.json") if profile == "data" else ("origin/state", f"data/video_maps/{vid}.json")
    text = git_show(branch, path)
    if text:
        return json.loads(text)
    if profile == "data":
        state = json.loads(git_show("origin/state-plotline", "data/plotline/state.json") or "{}")
        for day, e in state.get("days", {}).items():
            if e.get("video_id") == vid:
                script = json.loads(git_show("origin/state-plotline", f"data/plotline/{day}/script.json") or "{}")
                if script.get("scenes"):
                    return retention.estimate_map("long", title, [(f"scene {i + 1} ({s['visual'].get('type', '?')})", s["narration"])
                                                                  for i, s in enumerate(script["scenes"])], duration)
    return None


def curve_of(an, vid: str, start: date, end: date) -> tuple[list[tuple[float, float]], float | None]:
    resp = an.reports().query(ids="channel==MINE", startDate=str(start), endDate=str(end), metrics="audienceWatchRatio,relativeRetentionPerformance",
                              dimensions="elapsedVideoTimeRatio", filters=f"video=={vid}", sort="elapsedVideoTimeRatio").execute()
    rows = resp.get("rows", [])
    rel = [r[2] for r in rows if len(r) > 2 and r[2] is not None]
    return [(float(r[0]), float(r[1])) for r in rows], (sum(rel) / len(rel) if rel else None)


def main() -> None:
    env.load_env(ROOT / ".env")
    arg = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
    profiles = [arg("--profile", None)] if arg("--profile", None) else list(CHANNELS)
    min_views, days = int(arg("--min-views", 20)), int(arg("--days", 28))
    end = date.today() - timedelta(days=2)
    result: dict = {}
    for prof in profiles:
        creds = load_credentials(prof)
        yt, an = build("youtube", "v3", credentials=creds), build("youtubeAnalytics", "v2", credentials=creds)
        rows = an.reports().query(ids="channel==MINE", startDate=str(end - timedelta(days=days)), endDate=str(end), metrics="views",
                                  dimensions="video", sort="-views", maxResults=40).execute().get("rows", [])
        ids = [r[0] for r in rows if r[1] >= min_views][:15]
        meta = {m["id"]: m for m in (yt.videos().list(part="snippet,contentDetails", id=",".join(ids)).execute()["items"] if ids else [])}
        out = []
        print(f"\n===== {CHANNELS[prof]} =====")
        for r in rows:
            vid, views = r[0], int(r[1])
            m = meta.get(vid)
            if not m:
                continue
            dur, title = iso_seconds(m["contentDetails"]["duration"]), m["snippet"]["title"]
            try:
                pts, rel = curve_of(an, vid, date.fromisoformat(m["snippet"]["publishedAt"][:10]), end)
            except Exception as exc:  # noqa: BLE001
                print(f"{title}: no retention data ({str(exc)[:100]})")
                continue
            found = retention.analyse(pts, dur, load_map(prof, vid, title, dur), short=dur <= 62)
            found |= {"video": vid, "title": title, "views": views, "relative": None if rel is None else round(rel, 2)}
            out.append(found)
            print(retention.render(f"{title} [{'Short' if dur <= 62 else 'long'}]", found, views)
                  + ("" if rel is None else f"\n  vs similar videos: {rel:.2f} (1.0 = typical for this length)"))
        if not out:
            print(f"no video has {min_views}+ views in the last {days} days yet")
        result[prof] = out
    if "--json" in sys.argv:
        Path(arg("--json", "retention.json")).write_text(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
