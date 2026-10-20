"""Publish-time scheduling for the US/UK audience."""
from datetime import datetime, timedelta, timezone


def next_slot(hour_utc: int, now: datetime | None = None, min_lead_minutes: int = 20) -> datetime:
    """The next occurrence of hour_utc:00 UTC that is at least min_lead_minutes away
    (YouTube needs a publish time safely in the future)."""
    now = now or datetime.now(timezone.utc)
    slot = now.replace(hour=hour_utc, minute=0, second=0, microsecond=0)
    while slot - now < timedelta(minutes=min_lead_minutes):
        slot += timedelta(days=1)
    return slot


def rfc3339(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
