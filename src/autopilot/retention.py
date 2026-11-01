"""Audience-retention analysis: where do viewers leave, and what was on screen / being said at that moment?

YouTube's Analytics API gives, for one video, the share of viewers still watching at 100 evenly spaced points of its length
(dimension elapsedVideoTimeRatio, metric audienceWatchRatio). This module finds the hook leak and the steepest drop-offs in that curve and
maps each to the part of the video playing then, using a small "map" of the video written when it was made (segments with start and end
seconds, a label and the narration). Pure functions, no network: the API calls live in scripts/retention_report.py.

Idea borrowed (not code) from Jakeschincariol/youtube-agent-skill's retention tool, which does the same for a pasted Studio export."""
import itertools
import re

HOOK_SECONDS = 30.0
LEAK_OK, LEAK_BAD = 25.0, 40.0          # percentage points of the audience lost inside the hook window: below the first is healthy
SHORT_LEAK_OK, SHORT_LEAK_BAD = 40.0, 60.0   # a Short loses far more in its first seconds (viewers swipe), so its bands are wider


def video_map(kind: str, title: str, timings: list[dict], labels: list[str] | None = None) -> dict:
    """The map saved with a video: one segment per timed section (long videos) or per sentence (Shorts)."""
    segs = []
    if kind == "short":
        for sec in timings:
            for s in sec.get("sentences") or []:
                segs.append({"start": round(s["start"], 2), "end": round(s["end"], 2), "label": "", "text": s["text"][:300]})
    else:
        for i, sec in enumerate(timings):
            text = " ".join(s["text"] for s in sec.get("sentences") or [])
            segs.append({"start": round(sec["start"], 2), "end": round(sec["end"], 2),
                         "label": (labels[i] if labels and i < len(labels) else sec.get("heading", "")), "text": text[:1200]})
    return {"kind": kind, "title": title, "segments": segs}


def save_map(vmap: dict, video_id: str, folder) -> None:
    """Write the map of an uploaded video to `folder`/<video_id>.json. Never raises: a map is an extra and must not fail an upload."""
    import json
    from pathlib import Path

    try:
        Path(folder).mkdir(parents=True, exist_ok=True)
        (Path(folder) / f"{video_id}.json").write_text(json.dumps({**vmap, "video_id": video_id}))
    except Exception as exc:  # noqa: BLE001
        print(f"[retention] could not save the video map ({type(exc).__name__}: {exc})", flush=True)


def record(kind: str, title: str, timings: list[dict], video_id: str, folder, labels: list[str] | None = None, extra: dict | None = None) -> None:
    """Build the map from the video's timings and save it. Never raises: this is an extra and must not fail an upload."""
    try:
        save_map({**video_map(kind, title, timings, labels), **(extra or {})}, video_id, folder)
    except Exception as exc:  # noqa: BLE001
        print(f"[retention] no video map for {video_id} ({type(exc).__name__}: {exc})", flush=True)


def estimate_map(kind: str, title: str, pieces: list[tuple[str, str]], duration: float) -> dict:
    """A map for a video made before maps were saved: split `duration` over the (label, narration) pieces in proportion to their words.
    Good to within a few seconds, which is enough to say which scene a drop-off falls in."""
    words = [max(1, len(re.findall(r"\w+", t))) for _, t in pieces]
    total, t, segs = sum(words), 0.0, []
    for (label, text), w in zip(pieces, words, strict=True):
        span = duration * w / total
        segs.append({"start": round(t, 2), "end": round(t + span, 2), "label": label, "text": text[:1200]})
        t += span
    return {"kind": kind, "title": title, "segments": segs, "estimated": True}


def segment_at(vmap: dict | None, sec: float) -> dict | None:
    for s in (vmap or {}).get("segments", []):
        if s["start"] <= sec < s["end"]:
            return s
    segs = (vmap or {}).get("segments", [])
    return segs[-1] if segs and sec >= segs[-1]["end"] else None


def words_near(seg: dict, sec: float, n: int = 14) -> str:
    """About n words of the segment's narration around second `sec` (position estimated from word count)."""
    ws = seg["text"].split()
    if not ws:
        return ""
    span = max(0.01, seg["end"] - seg["start"])
    i = int(len(ws) * min(1.0, max(0.0, (sec - seg["start"]) / span)))
    a = max(0, i - n // 2)
    return " ".join(ws[a:a + n])


def analyse(curve: list[tuple[float, float]], duration: float, vmap: dict | None = None, top: int = 3, short: bool = False) -> dict:
    """curve: [(ratio of the video 0..1, share of viewers still watching)], any spacing. Returns the findings as plain numbers and text."""
    pts = sorted((r, w) for r, w in curve if w is not None)
    if len(pts) < 8 or duration <= 0:
        return {"error": "not enough retention data yet"}
    sec = [(r * duration, w * 100.0) for r, w in pts]
    start = sec[0][1] or 100.0
    window = min(HOOK_SECONDS, duration * 0.25)
    inside = [w for t, w in sec if t <= window] or [sec[0][1]]
    leak = max(0.0, start - min(inside))
    out: dict = {"duration": round(duration), "start_pct": round(start, 1), "hook_window_s": round(window),
                 "hook_leak_pp": round(leak, 1), "hook": "healthy" if leak < (SHORT_LEAK_OK if short else LEAK_OK) else "leaking" if leak < (SHORT_LEAK_BAD if short else LEAK_BAD) else "severe",
                 "end_pct": round(sec[-1][1], 1), "mid_pct": round(sec[len(sec) // 2][1], 1)}
    drops = []
    for (t0, w0), (t1, w1) in itertools.pairwise(sec):
        if t0 < 1.0:                                                         # the first instants are always noisy
            continue
        drops.append((w0 - w1, (t0 + t1) / 2, t1 - t0))
    cliffs, taken = [], []
    for d, t, gap in sorted(drops, reverse=True):
        if d < 0.8 or any(abs(t - u) < max(8.0, duration * 0.04) for u in taken):
            continue
        taken.append(t)
        seg = segment_at(vmap, t)
        cliffs.append({"at_s": round(t), "drop_pp": round(d, 1), "section": (seg or {}).get("label", ""), "said": words_near(seg, t) if seg else ""})
        if len(cliffs) == top:
            break
    out["cliffs"] = cliffs
    rises = sorted(((w1 - w0, (t0 + t1) / 2) for (t0, w0), (t1, w1) in itertools.pairwise(sec) if w1 - w0 > 0.6 and t0 > 3), reverse=True)[:2]
    out["rewatched"] = [{"at_s": round(t), "rise_pp": round(r, 1), "said": words_near(segment_at(vmap, t), t) if segment_at(vmap, t) else ""} for r, t in rises]
    return out


def mmss(sec: float) -> str:
    return f"{int(sec) // 60}:{int(sec) % 60:02d}"


def render(title: str, found: dict, views: int | None = None) -> str:
    if "error" in found:
        return f"{title}: {found['error']}"
    head = f"{title}" + (f" ({views} views)" if views is not None else "")
    if views is not None and views < 200:
        head += f"  [small sample: one viewer is about {100 / max(1, views):.1f} points, so treat the numbers as hints]"
    lines = [head, (f"  hook: {found['hook']}, {found['hook_leak_pp']} points lost in the first {found['hook_window_s']} s; "
                    f"{found['mid_pct']}% still watching at the half, {found['end_pct']}% at the end")]
    for c in found["cliffs"]:
        lines.append(f"  drop {c['drop_pp']} points at {mmss(c['at_s'])}" + (f" [{c['section']}]" if c["section"] else "") + (f": \"{c['said']}\"" if c["said"] else ""))
    for r in found["rewatched"]:
        lines.append(f"  replayed (+{r['rise_pp']}) around {mmss(r['at_s'])}" + (f": \"{r['said']}\"" if r["said"] else ""))
    return "\n".join(lines)
