"""Science Chaya daily flow on GitHub Actions.
  review : read Telegram button presses; green -> give the (already uploaded, private) video its publish time, red -> hold it
  render : build the next video of chaya/queue.json, upload it, schedule it for the next free 6 PM IST slot at once (no approval step) and tell Telegram
The ledger is data/chaya_state.json (kept on the `state-chaya` branch by scripts/chaya_state.sh); a failed step never publishes anything."""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
from autopilot import env, notify, upload
from chaya import ops

if os.environ.get("TELEGRAM_BOT_TOKEN_CHAYA"):      # a bot only Science Chaya uses: nothing else can read (and so swallow) the green and red presses
    os.environ["TELEGRAM_BOT_TOKEN"] = os.environ["TELEGRAM_BOT_TOKEN_CHAYA"]

STATE = ROOT / "data" / "chaya_state.json"
OUT = ROOT / "output" / "chaya"


def sync(what: str) -> None:
    subprocess.run([str(ROOT / "scripts" / "chaya_state.sh"), what], check=True, cwd=ROOT)


def load() -> dict:
    return json.loads(STATE.read_text()) if STATE.exists() else ops.empty_state()


def save(state: dict) -> None:
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1))


def ist(rfc: str) -> str:
    return datetime.fromisoformat(rfc.replace("Z", "+00:00")).astimezone(ops.IST).strftime("%a %d %b, %H:%M IST")


def review() -> None:
    sync("pull")
    state = load()
    presses = notify.button_presses(state.get("offset"))
    print(f"[chaya] {len(presses)} new Telegram updates (offset {state.get('offset')}), ledger: {[(k, v.get('status')) for k, v in state['items'].items() if v.get('status') in ('awaiting', 'held')]}", flush=True)
    if not presses:
        return
    chat = __import__("os").environ["TELEGRAM_CHAT_ID"]
    for p in presses:
        state["offset"] = p["update_id"] + 1
        done = ops.apply_press(state, p, chat, datetime.now(timezone.utc))
        if not done:
            continue
        what, arg = done
        if what == "approve":
            item = state["items"][arg]
            try:
                upload.schedule(item["youtube_id"], item["publish_at"], profile="ml")
                msg = f"Scheduled: {item['title']} for {ist(item['publish_at'])}."
            except Exception as exc:  # noqa: BLE001 - tell the owner, keep the video waiting
                item["status"] = "awaiting"
                item.pop("publish_at", None)
                msg = f"Could not schedule {item['title']} ({str(exc)[:120]}). Press green again later."
            notify.answer_press(p["callback_id"], "Green flag received")
            notify.send(msg)
        elif what == "hold":
            notify.answer_press(p["callback_id"], "Held")
            notify.send(f"Held: {state['items'][arg]['title']}. It stays private on YouTube. Send me a message with what to change and I will keep it as the note.")
        elif what == "note":
            notify.send(f"Note saved for {state['items'][arg]['title']}.")
        else:
            notify.answer_press(p["callback_id"], arg)
        save(state)
    save(state)
    sync("push")


def render() -> None:
    import importlib

    from chaya import build as chaya_build  # heavy imports only here
    from chaya import upload as chaya_upload
    env.load_env(ROOT / ".env")
    if (ROOT / "chaya" / "PAUSED").exists():          # the owner paused new renders (remove the file to resume)
        print("renders are paused: chaya/PAUSED exists")
        return
    sync("pull")
    state = load()
    queue = json.loads((ROOT / "chaya" / "queue.json").read_text())
    entry = ops.pick_next(queue, state)
    if not entry:
        print("nothing to render (queue empty or enough videos wait for a reply)")
        return
    mod = importlib.import_module(f"chaya.content_{entry['content']}")
    video = next(v for v in mod.VIDEOS if v["id"] == entry["id"])
    chaya_build.build(video, OUT, set())
    vid_id = chaya_upload.upload_private(entry["content"], OUT, entry["id"], None)
    sync("pull")                                                  # the ledger may have changed while this long job ran
    state = load()
    when = ops.next_slot(state, datetime.now(timezone.utc))      # no approval step: the video gets the next free 6 PM IST slot at once
    item = {"status": "uploaded", "youtube_id": vid_id, "title": video["title_ml"], "kind": "long" if video["orient"] == "wide" else "short"}
    state["items"][entry["id"]] = item
    try:
        upload.schedule(vid_id, when, profile="ml")
        item.update(status="approved", publish_at=when)
        line = f"Scheduled for {ist(when)}."
    except Exception as exc:  # noqa: BLE001 - keep it private and say so; the next run will not repeat it
        item["status"] = "awaiting"
        line = f"Uploaded private but could not schedule it ({str(exc)[:120]})."
    save(state)
    sync("push")
    notify.send(f"{video['title_ml']}\n{video['title_en']}\n\n{line}\nhttps://youtu.be/{vid_id}")


if __name__ == "__main__":
    {"review": review, "render": render}[sys.argv[1]]()
