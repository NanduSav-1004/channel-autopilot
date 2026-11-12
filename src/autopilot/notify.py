"""Phone alerts through a Telegram bot. Never raises: an alert problem must not break a video run."""
import json
import os
import urllib.parse
import urllib.request

from autopilot import net


def configured() -> bool:
    return bool(os.environ.get("TELEGRAM_BOT_TOKEN") and os.environ.get("TELEGRAM_CHAT_ID"))


def send(text: str) -> bool:
    """Send `text` to the owner's Telegram chat. Returns False (silently) if unconfigured or the call fails."""
    if not configured():
        return False
    token, chat = os.environ["TELEGRAM_BOT_TOKEN"], os.environ["TELEGRAM_CHAT_ID"]
    data = urllib.parse.urlencode({"chat_id": chat, "text": text[:3500], "disable_web_page_preview": "true"}).encode()
    try:
        with net.urlopen(urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=data), timeout=20) as r:
            return bool(json.load(r).get("ok"))
    except (OSError, ValueError):
        return False


def updates(offset: int | None = None) -> list[dict]:
    """New messages sent TO the bot, as [{"update_id", "chat_id", "text"}], oldest first. Only text messages. Empty on any problem."""
    if not configured():
        return []
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    url = f"https://api.telegram.org/bot{token}/getUpdates?timeout=0" + (f"&offset={offset}" if offset is not None else "")
    try:
        with net.urlopen(url, timeout=20) as r:
            res = json.load(r).get("result", [])
    except (OSError, ValueError):
        return []
    return [{"update_id": u["update_id"], "chat_id": str(u["message"]["chat"]["id"]), "text": u["message"].get("text", "")}
            for u in res if "message" in u]
