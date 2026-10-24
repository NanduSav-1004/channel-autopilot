"""Finds your Telegram chat id after you message your bot, and saves it to .env (nothing is printed).

usage: python scripts/telegram_chat_id.py     (needs TELEGRAM_BOT_TOKEN in .env, and a message sent to the bot)
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from autopilot.env import load_env

load_env()
token = os.environ["TELEGRAM_BOT_TOKEN"]
with urllib.request.urlopen(f"https://api.telegram.org/bot{token}/getUpdates", timeout=20) as r:
    updates = json.load(r)["result"]
chats = {u["message"]["chat"]["id"] for u in updates if "message" in u}
if len(chats) != 1:
    sys.exit(f"expected exactly one chat that has messaged the bot, found {len(chats)}; send the bot a message first")
env = Path(".env")
lines = [ln for ln in env.read_text().splitlines() if not ln.startswith("TELEGRAM_CHAT_ID=")]
env.write_text("\n".join(lines) + f"\nTELEGRAM_CHAT_ID={chats.pop()}\n")
print("saved TELEGRAM_CHAT_ID to .env")
