"""The channel's own first comment on each new video (approved 2026-11-02), and phone alerts for comments from viewers.

The comment is the video's comment question (engage.py), saved in the video map at upload. It is posted only once the video is PUBLIC (a
scheduled video cannot be commented on), by the channel itself and as itself: nothing pretends to be a viewer. YouTube's API cannot pin a
comment, so pinning stays a ten-second job in Studio. Replies to viewers are never posted from here: new comments are only sent to Telegram.

A small ledger (posted ids, failures, newest comment already announced) lives on its own branch, `state-comments`, so this hourly job never
touches the other state branches. All the YouTube calls take the `yt` client as an argument, so they are tested with a fake one."""
import json
import re
from datetime import datetime, timedelta, timezone

from autopilot import llm

MAX_PER_RUN = 8
MAX_TRIES = 3
ALERTS_PER_RUN = 6


def empty_ledger() -> dict:
    return {"posted": {}, "failed": {}, "seen_at": {}, "pending": {}, "next_id": 1, "tg_offset": None}


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


def post_first_comments(yt, maps: dict[str, dict], ledger: dict, log=print, send=None) -> int:
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
            if "insufficient" in str(exc).lower() or "scope" in str(exc).lower():
                # the login lacks the comment permission: not the video's fault, so it does not use up a try. The owner is told once.
                log(f"[comments] {vid}: the YouTube login lacks the permission to comment ({str(exc)[:100]}); will retry")
                if send and vid not in ledger.setdefault("notified", []):
                    ledger["notified"].append(vid)
                    send(f"The first comment on https://youtu.be/{vid} could not be posted: that channel's YouTube login lacks the comment permission. "
                         "It will be tried again after the login is renewed.")
                continue
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


DRAFT_PROMPT = """A viewer left this comment on the YouTube video "{title}" on the channel {channel}:
"{text}"

Classify it and draft a reply from the channel owner.
kind: "praise" (thanks, liking it), "question" (asks something), "criticism" (disagrees, points out a mistake or complains), "spam" (promotion, links,
nonsense, abuse) or "other".
Draft rules: 1 or 2 short sentences, warm and plain, in the same language as the comment. Thank them and respond to what they actually said; you may ask
one friendly follow-up question. Do NOT state new facts, numbers or claims, do NOT promise anything (future videos, corrections), no links, no emojis,
no hashtags. For a "question" that needs a factual answer, or for "criticism", or for "spam", return an EMPTY draft (the owner will write it).
Return JSON {{"kind": str, "draft": str}}"""


def make_draft(text: str, title: str, channel: str, gen=llm.generate_json) -> dict:
    """{"kind", "draft"} for a viewer comment. The draft is empty when it needs the owner (a factual question, criticism, spam) or the model is down."""
    try:
        got = gen(DRAFT_PROMPT.format(title=title, channel=channel, text=text[:600].replace('"', "'")))
        kind = str(got.get("kind", "other")).lower()
        draft = str(got.get("draft", "")).strip()
        bad = (not draft or len(draft) > 300 or "http" in draft.lower() or "www." in draft.lower() or kind in ("question", "criticism", "spam")
               or re.search(r"[\U0001F300-\U0001FAFF]", draft))
        return {"kind": kind if kind in ("praise", "question", "criticism", "spam", "other") else "other", "draft": "" if bad else draft}
    except (llm.LLMError, ValueError, AttributeError, TypeError):
        return {"kind": "other", "draft": ""}


def alert_text(profile_name: str, row: dict, title: str | None, pid: int | None = None, draft: dict | None = None) -> str:
    head = f"#{pid} " if pid else ""
    text = f"{head}New comment on {profile_name}: {title or row['video']}\n{row['author']}: {row['text'][:400]}\nhttps://youtube.com/watch?v={row['video']}&lc={row['id']}"
    if pid is None:
        return text
    if draft and draft["draft"]:
        return text + f"\n\nDraft reply ({draft['kind']}): {draft['draft']}\nSend  ok {pid}  to post it,  skip {pid}  to ignore it, or  {pid}: your own words  to post those."
    return text + f"\n\n({draft['kind'] if draft else 'other'}: no draft) Send  {pid}: your reply  to post it, or  skip {pid}."


def run_profile(yt, profile: str, name: str, maps: dict[str, dict], ledger: dict, send, log=print, first_run_quiet: bool = True, gen=llm.generate_json) -> None:
    """One channel: post due first comments, then announce new viewer comments through `send`, each with a numbered draft reply waiting for approval."""
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
        title = titles.get(row["video"])
        draft = make_draft(row["text"], title or "", name, gen)
        pid = ledger["next_id"]
        ledger["next_id"] = pid + 1
        ledger["pending"][str(pid)] = {"profile": profile, "thread": row["id"], "video": row["video"], "author": row["author"], "text": row["text"][:400],
                                      "draft": draft["draft"], "kind": draft["kind"], "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                      "status": "waiting"}
        send(alert_text(name, row, title, pid, draft))
    if len(fresh) > ALERTS_PER_RUN:
        send(f"{name}: {len(fresh) - ALERTS_PER_RUN} more new comments (see YouTube Studio).")
    if newest:
        ledger["seen_at"][profile] = newest


# ---- approvals: the owner answers the Telegram message ------------------------------------------------------------------
CMD = re.compile(r"^\s*(?:(?P<verb>ok|yes|post|skip|no)\s+#?(?P<n>\d+|all)|#?(?P<n2>\d+)\s*[:\-]\s*(?P<text>.+))\s*$", re.IGNORECASE | re.DOTALL)


def parse_command(text: str) -> tuple[str, str, str | None] | None:
    """('post'|'skip'|'custom', number-or-'all', custom text) from a message like 'ok 3', 'skip 3', 'ok all' or '3: thanks, glad it helped'."""
    m = CMD.match(text or "")
    if not m:
        return None
    if m.group("text"):
        return "custom", m.group("n2"), m.group("text").strip()[:500]
    return ("skip" if m.group("verb").lower() in ("skip", "no") else "post"), m.group("n"), None


def post_reply(yts: dict, item: dict, text: str):
    return yts[item["profile"]].comments().insert(part="snippet", body={"snippet": {"parentId": item["thread"], "textOriginal": text}}).execute()


def process_approvals(updates: list[dict], ledger: dict, yts: dict, owner_chat: str, send, log=print) -> int:
    """Apply the owner's commands. Only messages from `owner_chat` count. A reply is posted once (status moves waiting -> posted)."""
    done = 0
    for u in updates:
        ledger["tg_offset"] = u["update_id"] + 1
        if u["chat_id"] != str(owner_chat):
            continue
        cmd = parse_command(u["text"])
        if not cmd:
            continue
        verb, n, custom = cmd
        targets = [k for k, v in ledger["pending"].items() if v["status"] == "waiting"] if n == "all" else [n]
        for key in targets:
            item = ledger["pending"].get(key)
            if not item or item["status"] != "waiting":
                send(f"#{key}: nothing waiting with that number.")
                continue
            if verb == "skip":
                item["status"] = "skipped"
                send(f"#{key}: skipped.")
                continue
            text = custom if verb == "custom" else item["draft"]
            if not text:
                send(f"#{key}: there is no draft, so send  {key}: your reply  with your own words.")
                continue
            try:
                res = post_reply(yts, item, text)
                item.update(status="posted", reply_id=res.get("id", ""), posted=text)
                done += 1
                log(f"[comments] reply posted on #{key}: {text}")
                send(f"#{key}: reply posted: {text}")
            except Exception as exc:  # noqa: BLE001
                send(f"#{key}: could not post ({str(exc)[:150]}). It is still waiting.")
    return done


def expire_pending(ledger: dict, days: int = 7) -> None:
    """Forget waiting comments older than `days` (and old finished ones), so the ledger stays small."""
    now = datetime.now(timezone.utc)
    for key, v in list(ledger["pending"].items()):
        age = now - datetime.fromisoformat(v["at"])
        if age > timedelta(days=days if v["status"] == "waiting" else 3):
            del ledger["pending"][key]


def dumps(ledger: dict) -> str:
    return json.dumps(ledger, indent=1, sort_keys=True)
