"""The daily Plotline Data run: one long data story plus its Shorts, scheduled for US/UK viewers.

Every step is saved to data/plotline/ (kept between runs on the `state-plotline` branch), so a backup run continues where
an earlier one stopped instead of writing a new script: plan.json, script.json, shorts.json, and state.json with the
uploaded video ids. Run: python -m autopilot.plotline_daily [--live] [--privacy public]
"""
import argparse
import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

from autopilot import env, plotline, schedule

STATE = Path("data/plotline")
WORK = Path("output/plotline")
PUBLISH_HOUR_UTC = 19             # 7 pm in the UK, 2 to 3 pm on the US East Coast, 11 am to noon on the West Coast
SHORT_OFFSETS_HOURS = [3, 8, 14]  # after the long video: US evening, UK morning, US morning
SHORTS_PER_DAY = 3
CHANNEL = "@plotlinecharts"


def log(msg: str) -> None:
    print(msg, flush=True)


def load_state() -> dict:
    path = STATE / "state.json"
    return json.loads(path.read_text()) if path.exists() else {"days": {}}


def save_state(state: dict) -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / "state.json").write_text(json.dumps(state, indent=1))


def day_dir(day: str) -> Path:
    return STATE / day


def _json(path: Path):
    return json.loads(path.read_text()) if path.exists() else None


def recent_titles(state: dict, n: int = 40) -> list[str]:
    return [d["title"] for _, d in sorted(state["days"].items())[-n:] if d.get("title")]


def description(script: dict, bundle: dict, long_id: str | None = None) -> str:
    sources = sorted({s["source"] for s in bundle["series"].values()} | ({bundle["states"]["source"]} if bundle["states"] else set())
                     | ({bundle["owid"]["source"]} if bundle["owid"] else set()))
    parts = [str(script.get("description", "")).strip()]
    if long_id:
        parts.append(f"Full video: https://youtu.be/{long_id}")
    parts.append("Data sources:\n" + "\n".join(f"- {s}" for s in sources))
    parts.append("Every number in this video comes from the official data above. Charts are drawn from the data itself.")
    parts.append("Plotline Data videos are made with AI-assisted scripting and a synthetic voice. The data, the charts and the sources are real.")
    return "\n\n".join(p for p in parts if p)[:4900]


def retry_thumbnails(state: dict, live: bool) -> None:
    """Set the thumbnail of any recent uploaded video that has none yet (YouTube refuses custom thumbnails until the channel is
    phone-verified; once it is, the next run catches up). The thumbnails are kept with the state for this."""
    if not live:
        return
    from autopilot import upload

    changed = False
    for day, e in sorted(state["days"].items())[-7:]:
        thumb = day_dir(day) / "thumbnail.jpg"
        if e.get("video_id") and not e.get("thumbnail_set") and thumb.exists():
            try:
                upload.set_thumbnail(e["video_id"], thumb, profile="data")
                e["thumbnail_set"], changed = True, True
                log(f"[plotline] thumbnail set for {day} ({e['video_id']})")
            except Exception as exc:  # noqa: BLE001 - never a reason to stop the day's work
                log(f"[plotline] thumbnail for {day} still refused: {str(exc)[:120]}")
                break                    # the same refusal would repeat for every day
    if changed:
        save_state(state)


def run(live: bool, privacy: str, now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    day = now.strftime("%Y-%m-%d")
    state = load_state()
    retry_thumbnails(state, live)
    entry = state["days"].setdefault(day, {})
    shorts_done = [s for s in entry.get("shorts", []) if s.get("video_id")]
    if entry.get("video_id") and len(shorts_done) >= SHORTS_PER_DAY:
        return "today's Plotline video and Shorts are already up; nothing to do"
    d = day_dir(day)
    d.mkdir(parents=True, exist_ok=True)
    work = WORK / day

    with plotline.data_quota():
        plan = _json(d / "plan.json")
        if not plan:
            plan = plotline.pick_topic(recent=recent_titles(state))
            (d / "plan.json").write_text(json.dumps(plan, indent=1))
        log(f"[plotline] topic: {plan['title']} | data: {plan['series']} {plan.get('states') or ''} {plan.get('owid') or ''}")
        bundle = plotline.gather(plan)
        script = _json(d / "script.json")
        if not script:
            work.mkdir(parents=True, exist_ok=True)
            script = plotline.write_script(plan, bundle, log=log, draft_path=work / "draft.json")
            (d / "script.json").write_text(json.dumps(script, indent=1))
        entry["title"] = script["title"]
        save_state(state)

        # the long video
        if not entry.get("video_id"):
            video = plotline.make_video(script, bundle, work, log=log)
            thumb = plotline.make_thumbnail(script, bundle, work / "thumbnail.jpg")
            shutil.copy(thumb, d / "thumbnail.jpg")          # kept with the state, so a refused upload can be retried later
            if live:
                from autopilot import upload

                publish = schedule.rfc3339(schedule.next_slot(PUBLISH_HOUR_UTC, now)) if privacy == "public" else None
                vid = upload.insert_video(video, script["title"], description(script, bundle), script.get("tags") or [], privacy=privacy,
                                          publish_at=publish, profile="data", language="en")
                entry |= {"video_id": vid, "publish_at": publish}
                save_state(state)
                log(f"[plotline] uploaded https://youtu.be/{vid} (goes public {publish or 'now'})")
                try:
                    upload.set_thumbnail(vid, thumb, profile="data")
                    entry["thumbnail_set"] = True
                except Exception as exc:  # noqa: BLE001 - a missing thumbnail must not lose the upload
                    log(f"[plotline] WARNING: thumbnail not set: {exc}")
                save_state(state)
            else:
                log(f"[dry_run] would upload {video} with {thumb}")

        # the Shorts
        shorts = _json(d / "shorts.json")
        if not shorts:
            shorts = plotline.write_shorts(script, bundle, SHORTS_PER_DAY, log=log)
            (d / "shorts.json").write_text(json.dumps(shorts, indent=1))
    records = entry.setdefault("shorts", [])
    base = schedule.parse(entry["publish_at"]) if entry.get("publish_at") else now
    for i, sh in enumerate(shorts):
        if i < len(records) and records[i].get("video_id"):
            continue
        video = plotline.make_short(sh, bundle, work / f"short{i}", log=log)
        if not live:
            log(f"[dry_run] would upload Short {video}")
            continue
        from autopilot import upload

        when = base + timedelta(hours=SHORT_OFFSETS_HOURS[i % len(SHORT_OFFSETS_HOURS)])
        publish = schedule.rfc3339(max(when, now + timedelta(minutes=30))) if privacy == "public" else None
        vid = upload.insert_video(video, f"{sh['title']} #Shorts", description(script, bundle, entry.get("video_id")),
                                  ["shorts", "data", "charts"] + (script.get("tags") or [])[:6], privacy=privacy, publish_at=publish,
                                  profile="data", language="en")
        while len(records) <= i:
            records.append({})
        records[i] = {"title": sh["title"], "video_id": vid, "publish_at": publish}
        save_state(state)
        log(f"[plotline] Short {i + 1} uploaded https://youtu.be/{vid} (goes public {publish or 'now'})")
    if live and entry.get("video_id"):
        _notify(entry)
    return f"Plotline: {entry.get('title')}: video {entry.get('video_id') or '(not uploaded)'}, " \
           f"{len([s for s in records if s.get('video_id')])} Short(s)"


def _notify(entry: dict) -> None:
    from autopilot import notify
    from autopilot.cli import ist

    lines = [f"Plotline Data: uploaded {entry['title']!r}", f"https://youtu.be/{entry['video_id']}", f"Goes public: {ist(entry.get('publish_at'))}"]
    lines += [f"Short {i}: {ist(s.get('publish_at'))}" for i, s in enumerate(entry.get("shorts", []), 1) if s.get("video_id")]
    notify.send("\n".join(lines))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="really upload (otherwise only make the files)")
    ap.add_argument("--privacy", default="private", choices=["private", "unlisted", "public"])
    args = ap.parse_args()
    env.load_env(".env")
    print(run(args.live, args.privacy), flush=True)


if __name__ == "__main__":
    main()
