"""Plotline Data: one data-story video, from topic to finished MP4.

1. pick_topic: a language model chooses an everyday question and the catalogue data that answers it.
2. gather: the data is downloaded and turned into plain-English FACTS (datasets.facts).
3. write_script: the model writes scenes (narration + a chart request). check_script rejects any number that is not one
   of the facts (or a fair rounding of one), and any chart that asks for data we do not have; the model repairs it.
4. make_video: the narration is spoken, each chart is built FROM THE DATA (never from model output) and rendered for
   exactly as long as its narration, then music and voice are mixed in.
"""
import json
import math
import os
import re
import shutil
import subprocess
from contextlib import contextmanager
from pathlib import Path

from autopilot import datasets, llm, motion

MODELS = "gemini-3.5-flash,gemini-3.6-flash,gemini-3.8-flash,gemini-3.1-flash-lite"   # 3.8 is often overloaded
TARGET_WORDS = (750, 1050)          # about 5 to 7 minutes of narration
VOICE = {"engine": "kokoro", "name": "am_michael", "speed": 1.08}


@contextmanager
def data_quota():
    """LLM calls for this channel: its OWN Gemini key first (so the Brightwork channels' Gemini quota is never touched),
    then Groq."""
    key = os.environ.get("GEMINI_API_KEY_DATA")
    saved = {k: os.environ.get(k) for k in ("GEMINI_API_KEY", "GEMINI_MODELS", "LLM_PREFER")}
    if key:
        os.environ["GEMINI_API_KEY"], os.environ["GEMINI_MODELS"], os.environ["LLM_PREFER"] = key, MODELS, "gemini"
    else:
        os.environ.pop("GEMINI_API_KEY", None)
    try:
        yield
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


# ---- 1. topic -----------------------------------------------------------------------------------------------------------
def menu() -> str:
    cat = datasets.catalog()
    lines = [f"{k}: {v['name']} ({v['theme']})" for k, v in cat["fred"].items()]
    lines += [f"state:{k}: {v['name']}, for every US state ({v['theme']})" for k, v in cat["states"].items()]
    lines += [f"owid:{k}: {v['name']}, by country ({v['theme']})" for k, v in cat["owid"].items()]
    return "\n".join(lines)


PLAN_PROMPT = """You plan videos for "Plotline Data", a YouTube channel for viewers in the US and UK that answers everyday
questions with official data and animated charts ("Why are eggs so expensive?", "Which jobs disappeared?", "Is renting
getting worse?"). Pick ONE video idea that a curious adult would click, answerable with the data below.

Rules: no politics or parties, no investment or money advice, nothing about specific people. The question must be
genuinely interesting and the data must be able to answer it. Do not repeat these recent videos: {recent}

Available data (id: description):
{menu}

Return JSON {{"title": str (YouTube title, max 65 characters, curiosity-driven, honest), "angle": str (one sentence: the story
the data tells), "series": [1 to 4 ids from the list, without "state:" or "owid:"], "states": null or the state dataset key,
"owid": null or the owid key, "countries": null or a list of 5 to 8 country names (only with owid; include United States and
United Kingdom), "start": "YYYY" (first year to show; enough history for the story)}}"""


def pick_topic(gen=None, recent: list[str] | None = None) -> dict:
    gen = gen or llm.generate_json
    cat = datasets.catalog()
    prompt = PLAN_PROMPT.format(recent="; ".join(recent or []) or "none", menu=menu())
    for _ in range(3):
        plan = gen(prompt)
        plan["series"] = [s for s in plan.get("series") or [] if s in cat["fred"]][:4]
        if plan.get("states") not in cat["states"]:
            plan["states"] = None
        if plan.get("owid") not in cat["owid"]:
            plan["owid"], plan["countries"] = None, None
        if plan["series"] or plan["states"] or plan["owid"]:
            return plan
    raise ValueError("the topic planner chose no usable data")


# ---- 2. data ------------------------------------------------------------------------------------------------------------
def gather(plan: dict) -> dict:
    start = str(plan.get("start") or "2000")
    bundle: dict = {"start": start, "series": {}, "states": None, "owid": None, "facts": []}
    for sid in plan["series"]:
        s = datasets.series(sid)
        if not datasets.window(s["points"], start):
            start = s["points"][0][0][:4]
        bundle["series"][sid] = s
        bundle["facts"] += [f"[{sid}] {f}" for f in datasets.facts(s, start)]
    if plan.get("states"):
        st = datasets.state_values(plan["states"])
        bundle["states"] = st
        ranked = sorted(st["values"].items(), key=lambda kv: -kv[1])
        f = st["fmt"]
        bundle["facts"].append(f"[state:{st['key']}] {st['name']} by state, {st['year']} ({st['unit']}; source: {st['source']})")
        bundle["facts"] += [f"[state:{st['key']}] #{i + 1} highest: {datasets.STATE_NAMES[k]} {datasets.fmt(v, f)}"
                            for i, (k, v) in enumerate(ranked[:5])]
        bundle["facts"] += [f"[state:{st['key']}] #{len(ranked) - i} (lowest {i + 1}): {datasets.STATE_NAMES[k]} {datasets.fmt(v, f)}"
                            for i, (k, v) in enumerate(reversed(ranked[-5:]))]
    if plan.get("owid"):
        ow = datasets.owid(plan["owid"])
        names = [c for c in plan.get("countries") or [] if c in ow["rows"]]
        ow["countries"] = names
        bundle["owid"] = ow
        f = ow["fmt"]
        for c in names:
            rows = ow["rows"][c]
            last = rows[-1]
            line = f"[owid:{ow['slug']}] {c}: {datasets.fmt(last[1], f)} in {last[0]}"
            then = [r for r in rows if r[0] == 2000]
            if then:
                line += f" (in 2000: {datasets.fmt(then[0][1], f)})"
            bundle["facts"].append(line)
        bundle["facts"].insert(0, f"[owid:{ow['slug']}] {ow['name']} ({ow['unit']}; source: {ow['source']})")
    bundle["start"] = start
    return bundle


# ---- 3. script ----------------------------------------------------------------------------------------------------------
VISUALS = """Chart types (the "visual" of a scene). Numbers on screen are computed from the data, you only choose what to show:
- {"type": "title", "text": str, "highlight": [one or two words]}  -- the opening scene only
- {"type": "statement", "text": str (max 9 words, punchy), "highlight": [one word]}  -- a big text card for a key idea
- {"type": "line", "series": id, "start": "YYYY", "end": "YYYY" (optional), "annotate": ["max"|"min"]}  -- the series drawn over time (indexes are
  shown as percent change since "start")
- {"type": "counter", "series": id, "stat": "last"|"max"|"min"|"at", "date": "YYYY-MM" (with "at"), "start": "YYYY"}  -- one big
  number counting up; "max"/"min" look only from "start" on; use "at" + "date" to show the value of a particular month
- {"type": "compare", "series": id, "from": "YYYY" or "YYYY-MM", "to": "last" or "YYYY"}  -- then vs now (not for indexes)
- {"type": "bars", "series": [2 to 8 ids], "since": "YYYY"}  -- percent change of several series, ranked
- {"type": "states_bars", "order": "top"|"bottom", "n": 5 to 10}  -- ranking of states (needs the state data)
- {"type": "map"}  -- US map of the state data
- {"type": "countries_bars"}  -- the chosen countries ranked (needs the country data)"""

OUTLINE_PROMPT = """Plan a Plotline Data video (YouTube, US and UK viewers): "{title}".
The story: {angle}

FACTS available:
{facts}

Split the video into 6 acts that tell one story with a turn: 1 a hook with the most striking number, 2 the long view, 3 the
shock or the change, 4 WHY it happened (name the concrete, widely reported causes, e.g. "bird flu outbreaks forced farms to cull their hens",
"the 2008 financial crisis"; without any numbers that are not in the facts, not even written in words), 5 what it means for an ordinary household or a
comparison between the datasets, 6 the takeaway and an invitation to subscribe for more data stories.
Give every act its OWN facts: a number belongs to one act only (the headline number may come back once in the ending).
Spread the facts so the video moves forward and never repeats itself. No politics, no blame on parties or people, no
financial advice.

Return JSON {{"title": str (max 65 chars, honest, curiosity-driven), "description": str (2 short paragraphs for YouTube, no links),
"tags": [8 to 12 strings], "thumbnail": {{"number": str (one striking number exactly as in the facts, e.g. "$6.23" or "+326%"),
"words": str (2 to 4 words)}}, "acts": [{{"goal": str (what this act says, 1 to 2 sentences), "facts": [the facts this act uses, copied exactly]}}]}}"""

ACT_PROMPT = """You are writing act {n} of {total} of a Plotline Data video (YouTube, US and UK viewers): "{title}".
This act: {goal}

THIS ACT'S FACTS (build the act on these):
{act_facts}

All facts (the ONLY numbers you may say; you may round, e.g. "over $6", but never invent a number):
{facts}

The story so far (continue it; do NOT repeat its points, and do not re-quote these numbers: {used}):
{story}

Write {words} words of narration for this act, split into {scenes} scenes of 1 to 3 short sentences, each with one chart that
SHOWS what its narration says (the number spoken is the number on the chart; a cause or idea gets a statement card). Style: a
sharp, warm presenter (think Vox), short sentences, vivid but accurate; explain causes carefully and only with well-known,
widely reported facts. Write numbers as digits with symbols ($6.23, 4.5%, 2020). {extra}No "in this video", no politics, no
financial advice, no "title" chart (the video already has its title card).

{visuals}

Data ids you may use: {ids}

Return JSON {{"scenes": [{{"narration": str, "visual": {{...}}}}]}}"""

ACT_WORDS = (175, 7)          # words and scenes per act: 6 acts make about 1,000 words


NUM_RE = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?")


def _numbers(text: str) -> list[float]:
    return [float(m.group().replace(",", "")) for m in NUM_RE.finditer(text) if m.group().replace(",", "").replace(".", "").isdigit()]


def _roundings(x: float) -> set[float]:
    x = abs(x)
    out = {round(x, k) for k in range(4)}
    if x:
        mag = math.floor(math.log10(x))
        out |= {round(x, -mag + k) for k in range(3)}             # 1 to 3 significant figures: 326 -> 300, 330, 326
        out |= {math.floor(x * 10 ** (-mag + k)) / 10 ** (-mag + k) for k in range(3)}   # "over 300": rounded down
    return out


def allowed_numbers(bundle: dict) -> set[float]:
    ok: set[float] = set()
    for f in bundle["facts"]:
        for x in _numbers(f.split("] ", 1)[-1]):
            ok |= _roundings(x)
    return ok


def check_script(script: dict, bundle: dict) -> list[str]:
    problems = []
    ok = allowed_numbers(bundle)
    scenes = script.get("scenes") or []
    words = sum(len(s.get("narration", "").split()) for s in scenes)
    if words < TARGET_WORDS[0] * 0.9:
        problems.append(f"too short: {words} words; ADD about {TARGET_WORDS[0] - words + 60} words as NEW scenes (more context on causes, "
                        "what it means for a household, comparisons between the datasets, a recap before the ending)")
    seen: dict[float, list[int]] = {}
    for i, sc in enumerate(scenes, 1):
        for x in set(_numbers(sc.get("narration", ""))):
            if not (x.is_integer() and (1900 <= x <= 2100 or x <= 12)):
                seen.setdefault(x, []).append(i)
    for x, where in seen.items():
        if len(where) > 2:
            problems.append(f"scene {where[2]}: the number {x:g} is repeated in scenes {where}; say each number at most twice, use other facts")
    for i, sc in enumerate(scenes, 1):
        if i > 1 and (sc.get("visual") or {}).get("type") == "title":
            sc["visual"]["type"] = "statement"           # only the opening scene is a title card
        for x in _numbers(sc.get("narration", "")):
            if (x.is_integer() and (1900 <= x <= 2100 or x <= 12)) or abs(x) in ok:   # years and small counts are fine
                continue
            problems.append(f"scene {i}: the number {x:g} is not in the facts (use only the facts' numbers)")
        try:
            spec = compile_visual(sc.get("visual") or {}, bundle, 6.0)
        except (KeyError, ValueError, IndexError, TypeError) as exc:
            problems.append(f"scene {i}: bad visual {json.dumps(sc.get('visual'))}: {exc}")
            continue
        said = [x for x in _numbers(sc.get("narration", "")) if not (x.is_integer() and (1900 <= x <= 2100 or x <= 12))]
        if spec["type"] in ("counter", "compare") and said and not any(abs(x) in shown_numbers(spec) for x in said):
            problems.append(f"scene {i}: the narration says {', '.join(f'{x:g}' for x in said)} but the {spec['type']} chart shows "
                            f"something else; change the chart (e.g. counter with \"stat\": \"at\" and the month) so it shows that number")
    return problems


def write_script(plan: dict, bundle: dict, gen=None, tries: int = 3, log=print, draft_path: Path | None = None) -> dict:
    """An outline of 6 acts, then each act written on its own (short pieces come out at the right length), then the whole
    script checked; acts with problems are rewritten with the problems listed."""
    gen = gen or llm.generate_json
    ids = list(bundle["series"]) + (["state data"] if bundle["states"] else []) + (["country data"] if bundle["owid"] else [])
    facts = "\n".join(bundle["facts"])
    outline = gen(OUTLINE_PROMPT.format(title=plan["title"], angle=plan.get("angle", ""), facts=facts))
    acts = (outline.get("acts") or [])[:6]
    if len(acts) < 4:
        raise ValueError("the outline has too few acts")
    texts: list[list[dict]] = []
    for n, act in enumerate(acts, 1):
        extra = "Start with a hook in the first two sentences. " if n == 1 else \
                "Mention the source naturally once (for example \"according to the Bureau of Labor Statistics\"). " if n == 2 else \
                "End with a clear takeaway and ask viewers to subscribe for more data stories. " if n == len(acts) else ""
        texts.append(_write_act(gen, plan, act, n, len(acts), facts, [s for part in texts for s in part], extra, ids))
    script = {**{k: outline.get(k) for k in ("title", "description", "tags", "thumbnail")}, "scenes": [s for part in texts for s in part]}
    script["title"] = script.get("title") or plan["title"]
    if script["scenes"]:                                  # the opening scene is always the title card
        script["scenes"][0]["visual"] = {"type": "title", "text": script["title"], "highlight": []}
    return fix_script(script, plan, bundle, facts, ids, gen, tries, log, draft_path)


FIX_PROMPT = """You are fixing one scene of a Plotline Data video script: "{title}".
Scene before: {before}
THE SCENE: {scene}
Scene after: {after}

Problems to fix: {problems}

FACTS (the ONLY numbers you may say; never invent a number):
{facts}

Rewrite only this scene so it keeps its place in the story but has none of the problems. The chart must show the number the
narration says. {visuals}

Data ids you may use: {ids}

Return JSON {{"narration": str, "visual": {{...}}}}"""


def fix_script(script: dict, plan: dict, bundle: dict, facts: str, ids: list[str], gen=None, tries: int = 3, log=print,
               draft_path: Path | None = None) -> dict:
    """Check the script; rewrite only the scenes that fail (or add an act if it is too short); repeat."""
    gen = gen or llm.generate_json
    for attempt in range(tries + 1):
        problems = check_script(script, bundle)
        if draft_path:
            draft_path.write_text(json.dumps(script, indent=1))
        if not problems:
            return script
        if attempt == tries:
            break
        log(f"[plotline] script check {attempt + 1}: {len(problems)} problem(s): {problems[:4]}")
        by_scene: dict[int, list[str]] = {}
        for pr in problems:
            if m := re.match(r"scene (\d+):", pr):
                by_scene.setdefault(int(m.group(1)), []).append(pr.split(": ", 1)[1])
        scenes = script["scenes"]
        for i, issues in sorted(by_scene.items()):
            k = i - 1
            try:
                new = gen(FIX_PROMPT.format(title=script["title"], before=json.dumps(scenes[k - 1]) if k else "(none)", scene=json.dumps(scenes[k]),
                                            after=json.dumps(scenes[k + 1]) if k + 1 < len(scenes) else "(none)", problems="; ".join(issues),
                                            facts=facts, visuals=VISUALS, ids=", ".join(ids)))
            except llm.LLMError as exc:
                log(f"[plotline] could not fix scene {i}: {exc}")
                continue
            if new.get("narration") and isinstance(new.get("visual"), dict):
                scenes[k] = {"narration": new["narration"], "visual": new["visual"]}
        if any(pr.startswith("too short") for pr in problems):
            act = {"goal": "Add a new angle the video has not covered yet, using facts not quoted so far (another dataset, an earlier spike, "
                           "the last year's change, what it means for a household budget)", "facts": []}
            scenes[-2:-2] = _write_act(gen, plan, act, 6, 7, facts, scenes[:-2], "", ids)
    raise ValueError(f"the script still has problems: {check_script(script, bundle)[:5]}")


def _write_act(gen, plan: dict, act: dict, n: int, total: int, facts: str, done: list[dict], extra: str, ids: list[str]) -> list[dict]:
    story = " ".join(s["narration"] for s in done)[-3000:] or "(this is the start)"
    used = sorted({f"{x:g}" for s in done for x in _numbers(s["narration"]) if not (x.is_integer() and 1900 <= x <= 2100)})
    out = gen(ACT_PROMPT.format(n=n, total=total, title=plan["title"], goal=act.get("goal", ""), act_facts="\n".join(act.get("facts") or []) or "(choose)",
                                facts=facts, story=story, used=", ".join(used) or "none", words=ACT_WORDS[0], scenes=ACT_WORDS[1], extra=extra,
                                visuals=VISUALS, ids=", ".join(ids)))
    return [s for s in out.get("scenes") or [] if s.get("narration") and isinstance(s.get("visual"), dict)]


# ---- charts: from a scene's request to a motion.js spec, using only the data --------------------------------------------
def _short(name: str) -> str:
    name = re.sub(r"\s*\(.*?\)", "", re.sub(r"^Price of (a |an )?", "", name))
    return name[:1].upper() + name[1:]


def compile_visual(v: dict, bundle: dict, dur: float) -> dict:
    return round_shown(_compile(v, bundle, dur))


def _compile(v: dict, bundle: dict, dur: float) -> dict:
    t = v.get("type")
    base = {"duration": round(max(dur, 1.0), 3)}
    if t in ("title", "statement"):
        text = str(v["text"]).strip()
        if not text:
            raise ValueError("empty text")
        spec = {"type": "title", "title": text, "highlight": [h.lower() for h in v.get("highlight") or []]}
        if t == "title":
            spec["kicker"] = "Plotline Data"
        else:
            spec["size"] = 104
        return {**base, **spec}
    if t in ("line", "counter", "compare"):
        s = bundle["series"][v["series"]]
        pts = datasets.window(s["points"], str(v.get("start") or bundle["start"]), str(v["end"]) if v.get("end") else None) or s["points"]
        f, src = dict(s["fmt"]), s["source"]
        if s.get("index"):                       # an index only means something as a change
            if t == "compare":
                raise ValueError("compare cannot show an index; use line or counter")
            pts = [(d, datasets.pct(pts[0][1], x)) for d, x in pts]
            f = {"suffix": "%", "decimals": 0, "prefix": ""}
        if t == "line":
            notes = []
            for a in v.get("annotate") or []:
                p = max(pts, key=lambda q: q[1]) if a == "max" else min(pts, key=lambda q: q[1]) if a == "min" else None
                if p:
                    notes.append({"date": p[0], "label": f"{'Peak' if a == 'max' else 'Low'}: {datasets.fmt(p[1], f)}"})
            title = s["name"] + (f": change since {datasets.month_name(pts[0][0])}" if s.get("index") else "")
            span = int(pts[-1][0][:4]) - int(pts[0][0][:4])
            return {**base, "type": "line", "title": title, "series": pts, **_js_fmt(f), "annotations": notes, "source": src,
                    "yearStep": 1 if span <= 8 else 2 if span <= 16 else 5 if span <= 40 else 10, "draw": round(min(max(dur * 0.55, 2.5), 7), 2)}
        if t == "counter":
            stat = v.get("stat", "last")
            if stat == "at":
                p = datasets.at(datasets.window(s["points"], None) if not s.get("index") else pts, str(v["date"]))
                if s.get("index"):
                    raise ValueError("an index has no value to show at a date; use a line")
                stat = "last"
            else:
                p = {"last": pts[-1], "max": max(pts, key=lambda q: q[1]), "min": min(pts, key=lambda q: q[1])}[stat]
            label = ("Change in " + s["name"].lower() + f" since {pts[0][0][:4]}") if s.get("index") else \
                    {"last": s["name"], "max": "Peak " + s["name"].lower(), "min": "Lowest " + s["name"].lower()}[stat]
            spec = {**base, "type": "counter", "label": label[:44], "value": p[1], **_js_fmt(f), "sub": datasets.month_name(p[0]), "source": src}
            if not s.get("index") and p != pts[0]:
                c = datasets.pct(pts[0][1], p[1])
                spec |= {"badge": f"{c:+.0f}% since {pts[0][0][:4]}", "badgeColor": "coral" if c > 0 else "volt"}
            return spec
        a = datasets.at(s["points"], str(v["from"]))
        b = s["points"][-1] if str(v.get("to", "last")) == "last" else datasets.at(s["points"], str(v["to"]))
        if a[0] >= b[0]:
            raise ValueError("compare needs an earlier 'from' and a later 'to'")
        lab = lambda d: datasets.month_name(d)[:3] + " " + d[:4]
        return {**base, "type": "compare", "title": f"{s['name']}: {lab(a[0])} vs. {lab(b[0])}", "left": {"label": lab(a[0]), "value": a[1]},
                "right": {"label": lab(b[0]), "value": b[1]}, **_js_fmt(f), "verdict": f"{datasets.pct(a[1], b[1]):+.0f}%", "source": src}
    if t == "bars":
        ids = [i for i in v["series"] if i in bundle["series"]]
        if len(ids) < 2:
            raise ValueError("bars needs at least 2 of the video's series")
        since = str(v.get("since") or bundle["start"])
        items = []
        for i in ids:
            pts = datasets.window(bundle["series"][i]["points"], since)
            items.append({"label": _short(bundle["series"][i]["name"]), "value": round(datasets.pct(pts[0][1], pts[-1][1]), 1)})
        items.sort(key=lambda d: -d["value"])
        when = datasets.month_name(datasets.window(bundle["series"][ids[0]]["points"], since)[0][0])
        small = max(abs(d["value"]) for d in items) < 10
        srcs = sorted({bundle["series"][i]["source"] for i in ids})
        return {**base, "type": "bars", "title": f"Price change since {when}" if all(bundle["series"][i]["fmt"].get("prefix") == "$" for i in ids)
                else f"Change since {when}", "items": items, "suffix": "%", "prefix": "", "decimals": 1 if small else 0, "highlight": 0,
                "source": srcs[0] if len(srcs) == 1 else "; ".join(s.replace(" via FRED", "") for s in srcs) + " via FRED"}
    if t in ("states_bars", "map"):
        st = bundle["states"]
        if not st:
            raise ValueError("this video has no state data")
        if t == "map":
            top = max(st["values"], key=st["values"].get)
            return {**base, "type": "map", "title": f"{st['name']} by state, {st['year']}", "values": st["values"], **_js_fmt(st["fmt"]),
                    "legend": f"{st['name']}, {st['year']}", "highlight": top, "highlightName": datasets.STATE_NAMES[top], "source": st["source"]}
        n = max(5, min(10, int(v.get("n", 8))))
        ranked = sorted(st["values"].items(), key=lambda kv: kv[1], reverse=v.get("order", "top") != "bottom")[:n]
        word = "Highest" if v.get("order", "top") != "bottom" else "Lowest"
        return {**base, "type": "bars", "title": f"{word} {st['name'].lower()}: {n} states, {st['year']}",
                "items": [{"label": datasets.STATE_NAMES[k], "value": x} for k, x in ranked], **_js_fmt(st["fmt"]), "highlight": 0, "source": st["source"]}
    if t == "countries_bars":
        ow = bundle["owid"]
        if not ow or not ow["countries"]:
            raise ValueError("this video has no country data")
        items = sorted(({"label": c, "value": ow["rows"][c][-1][1]} for c in ow["countries"]), key=lambda d: -d["value"])
        year = max(ow["rows"][c][-1][0] for c in ow["countries"])
        hi = next((i for i, d in enumerate(items) if d["label"] in ("United States", "United Kingdom")), 0)
        return {**base, "type": "bars", "title": f"{ow['name']}, {year}", "items": items, **_js_fmt(ow["fmt"]), "highlight": hi, "source": ow["source"]}
    raise ValueError(f"unknown chart type {t!r}")


def shown_numbers(spec: dict) -> set[float]:
    """The headline numbers a chart displays (rounded as on screen), to check them against the narration."""
    f = {"prefix": spec.get("prefix", ""), "suffix": spec.get("suffix", ""), "decimals": spec.get("decimals", 0), "compact": spec.get("compact")}
    vals = []
    if spec["type"] == "counter":
        vals = [spec["value"]] + [float(m) for m in re.findall(r"[\d.]+", spec.get("badge", "").split("%")[0])]
    elif spec["type"] == "compare":
        vals = [spec["left"]["value"], spec["right"]["value"], datasets.pct(spec["left"]["value"], spec["right"]["value"])]
    elif spec["type"] == "line":
        vals = [spec["series"][-1][1]] + [x for a in spec.get("annotations", []) for x in _numbers(a["label"])]
    elif spec["type"] == "bars":
        vals = [d["value"] for d in spec["items"]]
    out: set[float] = set()
    for x in vals:
        out |= _roundings(x)                      # the exact value and its roundings ("34.9%" for a bar showing "-35%")
        for y in _numbers(datasets.fmt(abs(x), {**f, "prefix": "", "suffix": ""})):
            out |= _roundings(y)
    return out


def round_shown(spec: dict) -> dict:
    """Round every displayed value exactly as datasets.fmt would ($0.975 is "$0.97" in the script, so it must be on screen
    too; JavaScript would round it up)."""
    d = spec.get("decimals", 0)
    r = lambda x: float(f"{x:.{d}f}") if not spec.get("compact") else x
    for k in ("value",):
        if k in spec:
            spec[k] = r(spec[k])
    for side in ("left", "right"):
        if side in spec:
            spec[side]["value"] = r(spec[side]["value"])
    for item in spec.get("items", []):
        item["value"] = float(f"{item['value']:.{d}f}")
    return spec


def _js_fmt(f: dict) -> dict:
    return {"prefix": f.get("prefix", ""), "suffix": f.get("suffix", ""), "decimals": f.get("decimals", 0), "compact": bool(f.get("compact"))}


# ---- 4. video -----------------------------------------------------------------------------------------------------------
def make_video(script: dict, bundle: dict, out_dir: Path, log=print) -> Path:
    from autopilot import music, render, tts

    out_dir.mkdir(parents=True, exist_ok=True)
    scenes = script["scenes"]
    narration = out_dir / "narration.wav"
    timings_path = out_dir / "timings.json"
    if not timings_path.exists():
        engine = tts.build_engine(VOICE)
        timings = tts.synthesize_script({"sections": [{"heading": f"scene {i + 1}", "narration": s["narration"]}
                                                      for i, s in enumerate(scenes)]}, narration, engine)
        timings_path.write_text(json.dumps(timings))
    timings = json.loads(timings_path.read_text())
    total = timings[-1]["end"] + 1.6
    specs = []
    for i, sc in enumerate(scenes):
        start = 0.0 if i == 0 else timings[i]["start"]
        end = timings[i + 1]["start"] if i + 1 < len(timings) else total
        specs.append(compile_visual(sc["visual"], bundle, end - start))
    log(f"[plotline] {len(specs)} scenes, {total / 60:.1f} min; rendering charts")
    files = render_cached(specs, out_dir / "scenes")
    listing = out_dir / "scenes.txt"
    listing.write_text("".join(f"file '{p.resolve()}'\n" for p in files))
    video = out_dir / "charts.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(video)], check=True)
    beat = music.generate_beat(total + 2, out_dir / "music.wav", seed=len(script["title"]), style="lofi")
    mixed = out_dir / "mix.wav"
    log(f"[mix] audio: {render.mix_audio(narration, beat, mixed)}")
    final = out_dir / "final.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-i", str(mixed), "-filter_complex", "[1:a]apad[a]", "-map", "0:v",
                    "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.3f}", str(final)], check=True)
    return final


def render_cached(specs: list[dict], folder: Path) -> list[Path]:
    """Render scenes, reusing any scene already rendered with exactly the same spec (re-runs only redo what changed)."""
    import hashlib

    folder.mkdir(parents=True, exist_ok=True)
    stage = hashlib.sha1(b"".join((motion.STAGE / f).read_bytes() for f in ("motion.js", "theme.css"))).hexdigest()[:8]
    paths = [folder / f"{hashlib.sha1((stage + json.dumps(s, sort_keys=True)).encode()).hexdigest()[:16]}.mp4" for s in specs]
    todo = [(s, p) for s, p in zip(specs, paths, strict=True) if not p.exists()]
    if todo:
        tmp = folder / "new"
        for (_, p), f in zip(todo, motion.render_many([s for s, _ in todo], tmp), strict=True):
            f.rename(p)
        shutil.rmtree(tmp, ignore_errors=True)
    return paths


# ---- thumbnail ----------------------------------------------------------------------------------------------------------
THUMB = """<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: "Space Grotesk"; src: url("{stage}/fonts/SpaceGrotesk.ttf"); font-weight: 300 700; }}
html, body {{ margin: 0; background: #0b0d17; }}
</style></head><body>
<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720">
<defs>
 <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
 <radialGradient id="a" cx="20%" cy="25%" r="70%"><stop offset="0" stop-color="#39d2ff" stop-opacity=".35"/><stop offset="1" stop-color="#39d2ff" stop-opacity="0"/></radialGradient>
 <radialGradient id="c" cx="90%" cy="90%" r="60%"><stop offset="0" stop-color="#ff5c7a" stop-opacity=".35"/><stop offset="1" stop-color="#ff5c7a" stop-opacity="0"/></radialGradient>
 <linearGradient id="fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d4ff3a" stop-opacity=".35"/><stop offset="1" stop-color="#d4ff3a" stop-opacity="0"/></linearGradient>
</defs>
<rect width="1280" height="720" fill="#0b0d17"/><rect width="1280" height="720" fill="url(#a)"/><rect width="1280" height="720" fill="url(#c)"/>
<path d="{area}" fill="url(#fill)"/>
<path d="{line}" fill="none" stroke="#d4ff3a" stroke-width="12" stroke-linejoin="round" stroke-linecap="round" filter="url(#glow)"/>
<circle cx="{px}" cy="{py}" r="20" fill="#f5f3ee" filter="url(#glow)"/>
<text x="70" y="250" font-family="Space Grotesk" font-weight="700" font-size="{nsize}" fill="#d4ff3a" letter-spacing="-4" filter="url(#glow)">{number}</text>
<text x="76" y="352" font-family="Space Grotesk" font-weight="700" font-size="84" fill="#f5f3ee" letter-spacing="-1">{words}</text>
<rect x="76" y="388" width="140" height="12" rx="6" fill="#ff5c7a"/>
</svg></body></html>"""


def make_thumbnail(script: dict, bundle: dict, out: Path) -> Path:
    """The striking number in lime, a few words, and the main series as a glowing line rising behind them."""
    from html import escape

    th = script.get("thumbnail") or {}
    number, words = str(th.get("number") or ""), str(th.get("words") or script["title"])[:28]
    s = next(iter(bundle["series"].values()), None)
    pts = [v for _, v in datasets.window(s["points"], bundle["start"])] if s else [1, 2, 1.5, 3, 2.5, 4]
    step = max(1, len(pts) // 120)
    pts = pts[::step] + [pts[-1]]
    lo, hi = min(pts), max(pts)
    xy = [(560 + 680 * i / (len(pts) - 1), 650 - 430 * ((v - lo) / ((hi - lo) or 1))) for i, v in enumerate(pts)]
    line = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in xy)
    area = line + f" L{xy[-1][0]:.1f},720 L{xy[0][0]:.1f},720 Z"
    html = THUMB.format(stage=motion.STAGE.as_uri(), area=area, line=line, px=xy[-1][0], py=xy[-1][1], number=escape(number),
                        nsize=200 if len(number) <= 6 else 160, words=escape(words.upper()))
    tmp = out.with_suffix(".html")
    tmp.write_text(html)
    with motion.Browser() as b:
        page = b._b.new_page(viewport={"width": 1280, "height": 720})
        page.goto(tmp.as_uri())
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(200)
        page.screenshot(path=str(out), type="jpeg", quality=92)
    tmp.unlink()
    return out
