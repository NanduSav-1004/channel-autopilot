"""Helpers that turn a run of beats into one hand-made scene (no imports of content modules, so any module can use them)."""


def rich(video, first, last, kind, at=None, cams=None, **extra):
    """Make beats first..last (inclusive) one hand-made scene: kind slope|wave|moonland|cells|series|rainbow. `at` = {name: beat offset from `first`}, cams = [(beat offset, x, y, zoom[, cut])].
    The beats' own scenes inside the range are dropped, their cards stay."""
    beats = video["beats"]
    p = {"atb": dict(at or {}), **extra}
    if cams:
        p["cams"] = [{"atb": c[0], "x": c[1], "y": c[2], "z": c[3], **({"cut": True} if len(c) > 4 and c[4] else {})} for c in cams]
    beats[first]["scene"] = {"kind": kind, "p": p}
    for i in range(first + 1, last + 1):
        beats[i]["scene"] = None


def lab(video, first, last, mode, at=None, tags=None, cams=None, **extra):
    """A cut-away 'lab' scene over beats first..last. tags = [(beat offset, ml, en, x, y[, colour])]; at = {stage: beat offset}; modes: petrichor, firefly, goli, cassette, osmosis, lamp (see assets/motion/chaya_lab.js)."""
    p = {"mode": mode, "atb": dict(at or {}), "tags": [{"atb": t[0], "ml": t[1], "en": t[2], "x": t[3], "y": t[4], **({"col": t[5]} if len(t) > 5 else {})} for t in (tags or [])], **extra}
    if cams:
        p["cams"] = [{"atb": c[0], "x": c[1], "y": c[2], "z": c[3], **({"cut": True} if len(c) > 4 and c[4] else {})} for c in cams]
    video["beats"][first]["scene"] = {"kind": "lab", "p": p}
    for i in range(first + 1, last + 1):
        video["beats"][i]["scene"] = None
