"""Science Chaya daily flow on GitHub Actions.
  review : read Telegram button presses; green -> give the (already uploaded, private) video its publish time, red -> hold it
  render : build the next video of chaya/queue.json, upload it as private, send a small preview to Telegram with a green and a red button
The ledger is data/chaya_state.json (kept on the `state-chaya` branch by scripts/chaya_state.sh); a failed step never publishes anything."""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
from autopilot import env, notify, upload
from chaya import ops

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
    sync("pull")
    state = load()
    queue = json.loads((ROOT / "chaya" / "queue.json").read_text())
    entry = ops.pick_next(queue, state)
    if not entry:
        print("nothing to render (queue empty or enough videos wait for a reply)")
        return
    mod = importlib.import_module(f"chaya.content_{entry['content']}")
    video = next(v for v in mod.VIDEOS if v["id"] == entry["id"])
    final = chaya_build.build(video, OUT, set())
    vid_id = chaya_upload.upload_private(entry["content"], OUT, entry["id"], None)
    work = OUT / entry["id"]
    preview = work / "preview.mp4"
    secs = max(10.0, chaya_build.plan(video, [s for sec in json.loads((work / "timings.json").read_text()) for s in sec["sentences"]])[2])
    kbps = int(min(1500, 44 * 8 * 1000 / secs * 0.85))          # keep the preview under Telegram's 50 MB bot limit
    scale = "scale=-2:720" if video["orient"] == "wide" else "scale=-2:960"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(final), "-vf", scale, "-c:v", "libx264", "-b:v", f"{kbps}k", "-preset", "veryfast",
                    "-c:a", "aac", "-b:a", "64k", str(preview)], check=True)
    sync("pull")                                                  # the ledger may have changed while this long job ran
    state = load()
    state["items"][entry["id"]] = {"status": "awaiting", "youtube_id": vid_id, "title": video["title_ml"], "kind": "long" if video["orient"] == "wide" else "short"}
    save(state)
    sync("push")
    text = f"{video['title_ml']}\n{video['title_en']}\n\nPrivate on YouTube: https://youtu.be/{vid_id}\nGreen = schedule it for the next 6 PM slot, red = hold it."
    ok = notify.send_with_buttons(text, [("🟢 Green", f"chaya|ok|{entry['id']}"), ("🔴 Red", f"chaya|no|{entry['id']}")], video=preview)
    if not ok:
        notify.send_with_buttons(text, [("🟢 Green", f"chaya|ok|{entry['id']}"), ("🔴 Red", f"chaya|no|{entry['id']}")])


if __name__ == "__main__":
    {"review": review, "render": render}[sys.argv[1]]()
