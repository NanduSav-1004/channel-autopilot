"""The channel's own first comment on each new video (approved 2026-11-02), and phone alerts for comments from viewers.

The comment is the video's comment question (engage.py), saved in the video map at upload. It is posted only once the video is PUBLIC (a
scheduled video cannot be commented on), by the channel itself and as itself: nothing pretends to be a viewer. YouTube's API cannot pin a
comment, so pinning stays a ten-second job in Studio. Replies to viewers are never posted from here: new comments are only sent to Telegram.

A small ledger (posted ids, failures, newest comment already announced) lives on its own branch, `state-comments`, so this hourly job never
touches the other state branches. All the YouTube calls take the `yt` client as an argument, so they are tested with a fake one."""
import json
from datetime import datetime, timezone

MAX_PER_RUN = 8
MAX_TRIES = 3
ALERTS_PER_RUN = 6


def empty_ledger() -> dict:
    return {"posted": {}, "failed": {}, "seen_at": {}}


def public_ids(yt, ids: list[str]) -> set[str]:
    out: set[str] = set()
    for i in range(0, len(ids), 50):
        for item in yt.videos().list(part="status", id=",".join(ids[i:i + 50])).execute().get("items", []):
            if item["status"].get("privacyStatus") == "public":
                out.add(item["id"])
    return out


def due(maps: dict[str, dict], ledger: dict) -> list[str]:
    """Video ids that have a first comment waiting (and have not failed too often)."""
    return [vid for vid, m in maps.items() if m.get("comment") and vid not in ledger["posted"] and ledger["failed"].get(vid, 0) < MAX_TRIES]


def post_first_comments(yt, maps: dict[str, dict], ledger: dict, log=print) -> int:
    """Post the due first comments on videos that are public. Updates the ledger; returns how many were posted. Never raises for one video."""
    waiting = due(maps, ledger)
    if not waiting:
        return 0
    live = public_ids(yt, waiting)
    posted = 0
    for vid in waiting:
        if vid not in live or posted >= MAX_PER_RUN:
            continue
        text = maps[vid]["comment"].strip()[:500]
        try:
            res = yt.commentThreads().insert(part="snippet", body={"snippet": {"videoId": vid, "topLevelComment": {"snippet": {"textOriginal": text}}}}).execute()
            ledger["posted"][vid] = {"comment_id": res.get("id", ""), "at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "text": text}
            posted += 1
            log(f"[comments] first comment posted on https://youtu.be/{vid}: {text}")
        except Exception as exc:  # noqa: BLE001 - comments disabled, quota, a deleted video...
            ledger["failed"][vid] = ledger["failed"].get(vid, 0) + 1
            log(f"[comments] could not comment on {vid} ({str(exc)[:120]}); try {ledger['failed'][vid]}/{MAX_TRIES}")
    return posted


def new_viewer_comments(yt, channel_id: str, since: str | None) -> tuple[list[dict], str | None]:
    """Comments by other people on the channel's videos, newer than `since` (ISO time), oldest first, and the newest time seen."""
    res = yt.commentThreads().list(part="snippet", allThreadsRelatedToChannelId=channel_id, order="time", maxResults=30).execute()
    rows = []
    for t in res.get("items", []):
        top = t["snippet"]["topLevelComment"]["snippet"]
        if (top.get("authorChannelId") or {}).get("value") == channel_id:
            continue                                                       # our own first comment or reply
        rows.append({"video": top.get("videoId") or t["snippet"].get("videoId"), "author": top.get("authorDisplayName", ""),
                     "text": top.get("textOriginal") or top.get("textDisplay", ""), "at": top["publishedAt"], "id": t["id"]})
    newest = max((r["at"] for r in rows), default=since)
    fresh = sorted((r for r in rows if since is None or r["at"] > since), key=lambda r: r["at"])
    return fresh, newest


def alert_text(profile_name: str, row: dict, title: str | None) -> str:
    return f"New comment on {profile_name}: {title or row['video']}\n{row['author']}: {row['text'][:400]}\nhttps://youtube.com/watch?v={row['video']}&lc={row['id']}"


def run_profile(yt, profile: str, name: str, maps: dict[str, dict], ledger: dict, send, log=print, first_run_quiet: bool = True) -> None:
    """One channel: post due first comments, then announce new viewer comments through `send` (a function taking text)."""
    post_first_comments(yt, maps, ledger, log)
    ch = yt.channels().list(part="id", mine=True).execute()["items"][0]["id"]
    since = ledger["seen_at"].get(profile)
    fresh, newest = new_viewer_comments(yt, ch, since)
    if since is None and first_run_quiet:
        fresh = []                                                         # the first look only sets the starting point: no flood of old comments
    titles: dict[str, str] = {}
    ids = sorted({r["video"] for r in fresh if r["video"]})[:50]
    if ids:
        for item in yt.videos().list(part="snippet", id=",".join(ids)).execute().get("items", []):
            titles[item["id"]] = item["snippet"]["title"]
    for row in fresh[:ALERTS_PER_RUN]:
        send(alert_text(name, row, titles.get(row["video"])))
    if len(fresh) > ALERTS_PER_RUN:
        send(f"{name}: {len(fresh) - ALERTS_PER_RUN} more new comments (see YouTube Studio).")
    if newest:
        ledger["seen_at"][profile] = newest


def dumps(ledger: dict) -> str:
    return json.dumps(ledger, indent=1, sort_keys=True)
