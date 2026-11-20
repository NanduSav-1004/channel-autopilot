"""Phone alerts through a Telegram bot. Never raises: an alert problem must not break a video run."""
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

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


def _post(method: str, fields: dict, files: dict | None = None, timeout: float = 120) -> dict | None:
    """One Telegram Bot API call (form or multipart). None on any problem: an alert problem must not break a run."""
    if not configured():
        return None
    url = f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/{method}"
    try:
        if files:
            boundary = "----chaya" + os.urandom(8).hex()
            body = b""
            for k, v in fields.items():
                body += f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
            for k, (name, data) in files.items():
                body += f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"; filename="{name}"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode() + data + b"\r\n"
            body += f"--{boundary}--\r\n".encode()
            req = urllib.request.Request(url, data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
        else:
            req = urllib.request.Request(url, data=urllib.parse.urlencode(fields).encode())
        with net.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except (OSError, ValueError):
        return None


def send_with_buttons(text: str, buttons: list[tuple[str, str]], video=None) -> bool:
    """A message (with a small video preview when `video` is a path) and one row of inline buttons [(label, callback_data)]."""
    markup = json.dumps({"inline_keyboard": [[{"text": t, "callback_data": d} for t, d in buttons]]})
    fields = {"chat_id": os.environ.get("TELEGRAM_CHAT_ID", ""), "reply_markup": markup}
    if video:
        fields.update({"caption": text[:1000], "supports_streaming": "true"})
        res = _post("sendVideo", fields, {"video": ("preview.mp4", Path(video).read_bytes())})
    else:
        fields["text"] = text[:3500]
        res = _post("sendMessage", fields)
    return bool(res and res.get("ok"))


def button_presses(offset: int | None = None) -> list[dict]:
    """New button presses and plain messages sent to the bot, oldest first:
    [{"update_id", "chat_id", "callback_id", "data", "text"}] (data is set for a press, text for a message)."""
    if not configured():
        return []
    url = f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/getUpdates?timeout=0" + (f"&offset={offset}" if offset is not None else "")
    try:
        with net.urlopen(url, timeout=20) as r:
            res = json.load(r).get("result", [])
    except (OSError, ValueError) as exc:
        print(f"[telegram] could not read updates: {type(exc).__name__}: {str(exc)[:160]}", flush=True)
        return []
    out = []
    for u in res:
        if "callback_query" in u:
            cq = u["callback_query"]
            out.append({"update_id": u["update_id"], "chat_id": str(cq["message"]["chat"]["id"]), "callback_id": cq["id"], "data": cq.get("data", ""), "text": ""})
        elif "message" in u:
            out.append({"update_id": u["update_id"], "chat_id": str(u["message"]["chat"]["id"]), "callback_id": "", "data": "", "text": u["message"].get("text", "")})
    return out


def answer_press(callback_id: str, text: str) -> None:
    _post("answerCallbackQuery", {"callback_query_id": callback_id, "text": text[:190]})
