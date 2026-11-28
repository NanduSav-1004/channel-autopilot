"""Short helpers to write a Science Chaya storyboard as plain rows.
A row is (narration sentence, card Malayalam, card English[, scene]); the first row needs a scene, a later row gets one where the picture should change.
S(...) makes a scene from icons of the icon set, ST(...) a counting number, TX(...) a big word."""
from chaya.content_batch_shorts import outro, short
from chaya.content_monsoon import BL, BR, DK, GD, LF, OR, RD, SE, B
from chaya.dsl import LB, PT, C, I, T

COLS = [BR, LF, SE, OR, BL, GD, DK, RD]
SUBSCRIBE = "താഴെ കമന്റ് ചെയ്യൂ, ഇതുപോലുള്ള വീഡിയോകൾക്കായി സയൻസ് ചായ സബ്സ്ക്രൈബ് ചെയ്യൂ."


def S(icons, bg="dusk", pt=None, label=None, text=None, anim="float", **extra):
    """icons: one name or a list of up to three; pt: (kind, count, colour); label: (ml, en) on the first icon; text: a word under the picture."""
    names = [icons] if isinstance(icons, str) else list(icons)
    xs = {1: [0.5], 2: [0.3, 0.7], 3: [0.2, 0.5, 0.8]}[len(names)]
    size = {1: 6.5, 2: 4.6, 3: 3.6}[len(names)]
    layers = []
    for k, (nm, x) in enumerate(zip(names, xs)):
        kw = {"anim": anim}
        if k == 0 and label:
            kw["label"] = LB(label[0], label[1], OR, 380)
        layers.append(I(nm, x, 0.5, size, **kw))
    if pt:
        kind, n, col = pt
        layers.append(PT(kind, n, [0.3, 0.12, 0.7, 0.68], col, 7))
    if text:
        layers.append(T(text, 0.5, 0.87, 90, "#fff6e2" if bg in ("storm", "night", "dark", "soil") else "#2a1a10"))
    return C(layers, bg=bg, **extra)


def ST(value, suffix, ml, en, icon, **k):
    return {"kind": "stat", "p": {"value": value, "suffix": suffix, "ml": ml, "en": en, "icon": icon, **k}}


def TX(ml, en, icon, col=BR):
    return {"kind": "text", "p": {"ml": ml, "en": en, "icon": icon, "col": col}}


def rows_to_beats(rows):
    out = []
    for i, r in enumerate(rows):
        text, ml, en, *rest = r
        out.append(B(text, (ml, en, COLS[i % len(COLS)]) if ml else None, rest[0] if rest else None))
    return out


def sh(vid, title_ml, title_en, thumb_ml, thumb_en, rows, outro_ml, outro_en, outro_text):
    """A Short: rows, then the closing line card."""
    return short(vid, title_ml + " #Shorts", title_en, {"ml": thumb_ml, "en": thumb_en, "hero": "compose"}, rows_to_beats(rows) + [outro(outro_ml, outro_en, outro_text)])


def lg(vid, title_ml, title_en, thumb_ml, thumb_en, comment, comment_en, rows):
    """A long video: rows, then the question and the subscribe line."""
    beats = rows_to_beats(rows) + [B(comment, None, {"kind": "outro", "p": {"ml": comment, "en": comment_en}}), B(SUBSCRIBE)]
    return {"id": vid, "orient": "wide", "mood": "curious", "title_ml": title_ml, "title_en": title_en, "thumb": {"ml": thumb_ml, "en": thumb_en, "hero": "compose"}, "comment": comment, "beats": beats}


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
