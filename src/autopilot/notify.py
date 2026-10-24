"""Phone alerts through a Telegram bot. Never raises: an alert problem must not break a video run."""
import json
import os
import urllib.parse
import urllib.request


def configured() -> bool:
    return bool(os.environ.get("TELEGRAM_BOT_TOKEN") and os.environ.get("TELEGRAM_CHAT_ID"))


def send(text: str) -> bool:
    """Send `text` to the owner's Telegram chat. Returns False (silently) if unconfigured or the call fails."""
    if not configured():
        return False
    token, chat = os.environ["TELEGRAM_BOT_TOKEN"], os.environ["TELEGRAM_CHAT_ID"]
    data = urllib.parse.urlencode({"chat_id": chat, "text": text[:3500], "disable_web_page_preview": "true"}).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=data), timeout=20) as r:
            return bool(json.load(r).get("ok"))
    except (OSError, ValueError):
        return False
