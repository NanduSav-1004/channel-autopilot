"""The decisions of the Science Chaya daily flow, without any network: which video is next, when it goes live, what a Telegram button press does."""
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))
SLOT_HOUR = 18            # one video a day, 6 PM IST
MAX_AWAITING = 1          # videos waiting for a green or red flag at once
LEAD = timedelta(hours=3)  # a slot must be at least this far ahead (YouTube needs a future time)


def empty_state() -> dict:
    return {"offset": None, "items": {}}


def next_slot(state: dict, now: datetime) -> str:
    """The first 6 PM IST slot after every slot already given, and at least LEAD from now. RFC 3339 UTC."""
    taken = [datetime.fromisoformat(v["publish_at"].replace("Z", "+00:00")) for v in state["items"].values() if v.get("publish_at") and v.get("status") in ("approved", "uploaded")]
    day = (max(taken).astimezone(IST).date() + timedelta(days=1)) if taken else now.astimezone(IST).date()
    while True:
        slot = datetime(day.year, day.month, day.day, SLOT_HOUR, tzinfo=IST)
        if slot - now >= LEAD:
            return slot.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        day += timedelta(days=1)


def pick_next(queue: list[dict], state: dict) -> dict | None:
    """The first queue entry ({"content", "id"}) that is not in the state yet, unless too many wait for a reply."""
    if sum(1 for v in state["items"].values() if v.get("status") == "awaiting") >= MAX_AWAITING:
        return None
    return next((q for q in queue if q["id"] not in state["items"]), None)


def apply_press(state: dict, press: dict, chat_id: str, now: datetime) -> tuple[str, str] | None:
    """Apply one Telegram update. Returns (what, text for the reply) or None if it is not for us.
    Buttons carry data 'chaya|ok|<id>' or 'chaya|no|<id>'; a plain message is kept as the note of the latest held video."""
    if press["chat_id"] != str(chat_id):
        return None
    items = state["items"]
    if press["data"].startswith("chaya|"):
        _, what, vid = press["data"].split("|", 2)
        item = items.get(vid)
        if not item:
            return ("unknown", "I do not know that video any more.")
        if item["status"] != "awaiting":
            return ("again", f"Already {item['status']}.")
        if what == "ok":
            item["publish_at"] = next_slot(state, now)
            item["status"] = "approved"
            return ("approve", vid)
        item["status"] = "held"
        return ("hold", vid)
    if press["text"]:
        held = [k for k, v in items.items() if v.get("status") == "held"]
        if held:
            items[held[-1]]["note"] = press["text"][:1000]
            return ("note", held[-1])
    return None
