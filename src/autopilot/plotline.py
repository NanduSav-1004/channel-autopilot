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
MUSIC_STYLE = "ambient"     # the soft pad the user prefers (as on Brightwork); "lofi", "upbeat" or "pulse" are beat styles from music.py


def bundle_mood(bundle: dict) -> str:
    """The mood of a video's music from the theme of its data (housing and money mysterious, jobs and food curious, anything else plain)."""
    from autopilot import audio

    first = next(iter(bundle["series"].values()), None) or bundle.get("states") or bundle.get("owid") or {}
    return audio.mood_for_theme(first.get("theme"))


def make_bed(seconds: float, out: Path, seed: int, mood: str = "plain") -> Path:
    from autopilot import audio, music

    return audio.generate_ambient(seconds, out, seed=seed, mood=mood) if MUSIC_STYLE == "ambient" else music.generate_beat(seconds, out, seed=seed, style=MUSIC_STYLE)


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
United Kingdom), "owid2": null or a SECOND owid key to set against the first in a scatter plot (e.g. GDP per person against life
expectancy), "states2": null or a SECOND state dataset key to set against "states", "start": "YYYY" (first year to show; enough
history for the story)}}"""


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
        if not plan["owid"] or plan.get("owid2") not in cat["owid"] or plan.get("owid2") == plan["owid"]:
            plan["owid2"] = None
        if not plan["states"] or plan.get("states2") not in cat["states"] or plan.get("states2") == plan["states"]:
            plan["states2"] = None
        if plan["series"] or plan["states"] or plan["owid"]:
            return plan
    raise ValueError("the topic planner chose no usable data")


# ---- 2. data ------------------------------------------------------------------------------------------------------------
def gather(plan: dict) -> dict:
    start = str(plan.get("start") or "2000")
    bundle: dict = {"start": start, "series": {}, "states": None, "owid": None, "facts": [], "pair": None}
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
        bundle["facts"].append(f"[countries] {ow['name']} ({ow['unit']}; source: {ow['source']}); each country below is a series you can chart")
        world, wyear = datasets.world_values(ow)
        if world:
            rank = sorted(world.items(), key=lambda kv: -kv[1])
            fm = lambda n: n.replace("United States of America", "United States")
            bundle["facts"] += [f"[world-map] #{i + 1} highest in {wyear}: {fm(k)} {datasets.fmt(x, ow['fmt'])}" for i, (k, x) in enumerate(rank[:5])]
            bundle["facts"] += [f"[world-map] #{len(rank) - i} (lowest {i + 1}) in {wyear}: {fm(k)} {datasets.fmt(x, ow['fmt'])}" for i, (k, x) in enumerate(reversed(rank[-5:]))]
            bundle["facts"].append(f"[world-map] a world map of {len(world)} countries for {wyear} is available (visual world_map)")
        for c in names:                      # every country is a series like any other, so lines, counters and comparisons work
            sid = re.sub(r"[^a-z0-9]+", "-", c.lower()).strip("-")
            s = {"id": sid, "name": f"{ow['name']} in {c}", "label": c, "unit": ow["unit"], "fmt": ow["fmt"], "theme": ow["theme"],
                 "source": ow["source"], "yearly": True,
                 "points": [(f"{y}-01-01", v) for y, v in sorted(ow["rows"][c])]}
            bundle["series"][sid] = s
            first_year = max(int(start), int(s["points"][0][0][:4]))
            bundle["facts"] += [f"[{sid}] {x}" for x in datasets.facts(s, str(first_year))]
    bundle["pair"] = None
    if plan.get("states") and plan.get("states2"):
        st2 = datasets.state_values(plan["states2"])
        common = [k for k in bundle["states"]["values"] if k in st2["values"]]
        if len(common) >= 30:
            bundle["states2"] = st2
            bundle["pair"] = {"kind": "states", "names": {k: datasets.STATE_NAMES[k] for k in common},
                              "x": {k: bundle["states"]["values"][k] for k in common}, "y": {k: st2["values"][k] for k in common},
                              "xmeta": bundle["states"], "ymeta": st2, "year": bundle["states"]["year"]}
    if plan.get("owid") and plan.get("owid2"):
        ow2 = datasets.owid(plan["owid2"])
        pair = datasets.pair_countries(bundle["owid"], ow2)
        if pair:
            bundle["owid2"] = ow2
            bundle["pair"] = {"kind": "countries", **pair, "xmeta": bundle["owid"], "ymeta": ow2, "highlight": bundle["owid"].get("countries") or []}
    if bundle["pair"]:
        pr = bundle["pair"]
        r = datasets.correlation([pr["x"][k] for k in pr["x"]], [pr["y"][k] for k in pr["x"]])
        xm, ym = pr["xmeta"], pr["ymeta"]
        bundle["facts"].append(f"[scatter] {xm['name']} against {ym['name']}, {pr['year']}, {len(pr['x'])} {pr['kind']}: they move "
                               f"{'together' if r > 0 else 'in opposite directions'} (correlation {r:+.2f}); sources: {xm['source']}")
        keys = pr.get("highlight") or [k for k, _ in sorted(pr["x"].items(), key=lambda kv: kv[1])][:2] + [k for k, _ in sorted(pr["x"].items(), key=lambda kv: -kv[1])][:3]
        for k in keys:
            if k in pr["x"]:
                name = pr["names"].get(k, k)
                bundle["facts"].append(f"[scatter] {name}: {xm['name']} {datasets.fmt(pr['x'][k], xm['fmt'])}, {ym['name']} {datasets.fmt(pr['y'][k], ym['fmt'])}")
    bundle["start"] = start
    return bundle


# ---- 3. script ----------------------------------------------------------------------------------------------------------
VISUALS = """Chart types (the "visual" of a scene). Numbers on screen are computed from the data, you only choose what to show.
CHOOSE BY WHAT THE SENTENCE IS ABOUT, and use a wide variety: a good video uses at least 6 different types and never leans on one.
The striking ones (kpi, waffle, gauge, donut, heatmap, race, map, world_map, scatter, stacked) fit only twice per video; multiline, slope, compare and bars three
times; line and counter are the workhorses. Put the right chart on the right sentence (a ranking over years: race; "how many in 100": waffle;
"where does it stand historically": gauge; a split into parts: donut; many things compared over time: multiline).
- {"type": "title", "text": str, "highlight": [one or two words]}  -- the opening scene only
- {"type": "statement", "text": str (max 9 words, punchy), "highlight": [one word]}  -- a big text card for a key idea or a cause
- {"type": "line", "series": id, "start": "YYYY", "end": "YYYY" (optional), "annotate": ["max"|"min"]}  -- ONE series over time
  (indexes are shown as percent change since "start")
- {"type": "multiline", "series": [2 to 6 ids], "since": "YYYY", "as": "change"|"value"}  -- SEVERAL series racing on one chart, to
  compare how they moved ("change" = percent change since "since"; "value" needs the same unit and no index)
- {"type": "counter", "series": id, "stat": "last"|"max"|"min"|"at", "date": "YYYY-MM" (with "at"), "start": "YYYY"}  -- one big
  number counting up; "max"/"min" look only from "start" on; use "at" + "date" to show the value of a particular month.
  For an INDEX series (the facts say so) "at" and "compare" are NOT possible: use "last"/"max"/"min" (shown as percent change since
  "start") or a line
- {"type": "compare", "series": id, "from": "YYYY" or "YYYY-MM", "to": "last" or "YYYY"}  -- then vs now for ONE series (not for indexes)
- {"type": "slope", "series": [2 to 8 ids, same unit, no index], "from": "YYYY", "to": "last"}  -- THEN vs NOW for many items at once
  (a dot for then, a dot for now, joined)
- {"type": "bars", "series": [2 to 8 ids], "since": "YYYY"}  -- percent change of several series, ranked
- {"type": "race", "series": [3 to 10 ids, same unit], "since": "YYYY"}  -- animated ranking that reorders year by year (best for
  countries or sectors that overtake each other)
- {"type": "kpi", "series": [2 to 4 ids]}  -- a dashboard of big numbers with change badges and trend lines (good for an overview)
- {"type": "waffle", "series": id (a percent), "stat": "last"|"max"|"min"}  -- 100 squares filling up: "x out of 100" (only for series in %)
- {"type": "gauge", "series": id, "start": "YYYY"}  -- where today's value stands between the lowest and highest since "start"
- {"type": "donut", "series": [2 to 7 ids that add up, e.g. job sectors]}  -- how a total splits into parts (only series marked additive)
- {"type": "stacked", "series": [3 to 7 additive ids], "as": "share"|"total", "since": "YYYY"}  -- stacked area: how the parts of a total
  shift over time ("share" shows each part's percent of the whole)
- {"type": "scatter", "trails": true|false}  -- two measures against each other, one dot per country or state, the highlighted ones
  labelled and (with trails) traced over the years; only when the video has a second dataset ("owid2" / "states2")
- {"type": "heatmap", "series": id (monthly), "years": 3 to 16}  -- a grid of year by month showing monthly percent changes
- {"type": "states_bars", "order": "top"|"bottom", "n": 5 to 10}  -- ranking of states (needs the state data)
- {"type": "map"}  -- US map of the state data
- {"type": "world_map", "highlight": country (optional)}  -- world map of the country data (needs the country data)
- {"type": "countries_bars"}  -- the chosen countries ranked, latest year (needs the country data); at most twice per video"""

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


def _small(x: float) -> bool:
    """Years and small counts ("3 reasons") need no source."""
    return x.is_integer() and (1900 <= x <= 2100 or x <= 12)


def scene_problems(sc: dict, bundle: dict, ok: set[float] | None = None) -> list[str]:
    """What is wrong with one scene: numbers that are not in the facts, a chart that cannot be built or that does not show
    the number being spoken. (Messages come without the "scene N:" prefix.)"""
    ok = allowed_numbers(bundle) if ok is None else ok
    out = [f"the number {x:g} is not in the facts (use only the facts' numbers)"
           for x in _numbers(sc.get("narration", "")) if not _small(x) and abs(x) not in ok]
    try:
        spec = compile_visual(sc.get("visual") or {}, bundle, 6.0)
    except (KeyError, ValueError, IndexError, TypeError) as exc:
        return out + [f"bad visual {json.dumps(sc.get('visual'))}: {exc}"]
    said = [x for x in _numbers(sc.get("narration", "")) if not _small(x)]
    if spec["type"] in ("counter", "compare", "waffle", "gauge") and said and not any(abs(x) in shown_numbers(spec) for x in said):
        out.append(f"the narration says {', '.join(f'{x:g}' for x in said)} but the {spec['type']} chart shows "
                   "something else; change the chart (e.g. counter with \"stat\": \"at\" and the month) so it shows that number")
    return out


def check_script(script: dict, bundle: dict, min_words: int | None = None) -> list[str]:
    problems = []
    ok = allowed_numbers(bundle)
    scenes = script.get("scenes") or []
    words = sum(len(s.get("narration", "").split()) for s in scenes)
    need = TARGET_WORDS[0] if min_words is None else min_words
    if words < need * 0.9:
        problems.append(f"too short: {words} words; ADD about {need - words + 60} words as NEW scenes (more context on causes, "
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
        problems += [f"scene {i}: {pr}" for pr in scene_problems(sc, bundle, ok)]
    shown: dict[str, list[int]] = {}                       # the same chart again and again is dull: at most twice
    for i, sc in enumerate(scenes, 1):
        try:
            spec = compile_visual(sc.get("visual") or {}, bundle, 6.0)
        except (KeyError, ValueError, IndexError, TypeError):
            continue
        if spec["type"] != "title":
            shown.setdefault(json.dumps({k: v for k, v in spec.items() if k != "duration"}, sort_keys=True), []).append(i)
    kinds: dict[str, list[int]] = {}
    for i, sc in enumerate(scenes, 1):
        k = (sc.get("visual") or {}).get("type")
        if k not in ("title", "statement", None):
            kinds.setdefault(k, []).append(i)
    charts = sum(len(w) for w in kinds.values())
    for k, where in kinds.items():
        cap = RARE_CAP if k in RARE else COMMON_CAP if k in COMMON else max(4, math.ceil(0.22 * charts))
        if len(where) > cap and charts >= 10:
            problems.append(f"scene {where[cap]}: chart type '{k}' is already used {cap} times; pick a different type from the menu "
                            "(multiline, slope, race, kpi, waffle, gauge, donut, heatmap, bars, compare, counter ... whichever fits the sentence)")
    for where in shown.values():
        if len(where) > 2:
            problems.append(f"scene {where[2]}: the same chart is already shown in scenes {where[:2]}; use a different chart, series or period")
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


RARE = ("kpi", "waffle", "gauge", "donut", "heatmap", "race", "world_map", "map", "scatter", "stacked")      # striking charts: twice per video at most
COMMON_CAP, RARE_CAP = 3, 2
COMMON = ("multiline", "slope", "compare", "bars", "states_bars", "countries_bars")
SOFT = ("is repeated", "the same chart", "chart type")        # style problems: worth a rewrite, never worth losing the video
SENT_RE = re.compile(r"(?<=[.!?])\s+")


def _safe_visual(sc: dict, bundle: dict, k: int = 0) -> dict:
    """A chart that always works for this scene: a line of the series it was about (else the video's first series), or the
    state / country ranking, or a plain text card of its first sentence."""
    sid = (sc.get("visual") or {}).get("series")
    sid = sid if isinstance(sid, str) and sid in bundle["series"] else next(iter(bundle["series"]), None)
    if sid:
        first = int(bundle["start"])
        last = int(bundle["series"][sid]["points"][-1][0][:4])
        return {"type": "line", "series": sid, "start": str(first + (last - first) * (k % 3) // 4)}   # a different stretch each time
    if bundle["states"]:
        return {"type": "states_bars", "order": "top", "n": 8}
    if bundle["owid"] and bundle["owid"]["countries"]:
        return {"type": "countries_bars"}
    first = " ".join(SENT_RE.split(sc.get("narration", "").strip())[0].split()[:9])
    return {"type": "statement", "text": first or "The data", "highlight": []}


def settle(script: dict, bundle: dict, min_words: int | None = None, log=print) -> dict:
    """LAST RESORT, no language model: when a scene is still wrong after the rewrites, repair it by rule so that the day's video
    is never lost to one stubborn scene. A sentence with a number that is not in the facts is cut (its scene is dropped if
    nothing is left); a chart that cannot be built or does not show the spoken number becomes a plain line chart of the same data.
    Repeated numbers are allowed. Raises ValueError only if the script is then too short to be a video."""
    ok = allowed_numbers(bundle)
    kept, cut, swapped = [], 0, 0
    for sc in script["scenes"]:
        sentences = SENT_RE.split(sc.get("narration", "").strip())
        good = [s for s in sentences if all(_small(x) or abs(x) in ok for x in _numbers(s))]
        cut += len(sentences) - len(good)
        if not good:
            continue
        sc = {**sc, "narration": " ".join(good)}
        if any(not pr.startswith("the number") for pr in scene_problems(sc, bundle, ok)):
            sc["visual"] = _safe_visual(sc, bundle, swapped)
            swapped += 1
        kept.append(sc)
    if kept:
        kept[0]["visual"] = {"type": "title", "text": script["title"], "highlight": []}
    script["scenes"] = kept
    words = sum(len(s["narration"].split()) for s in kept)
    log(f"[plotline] settled by rule: {cut} sentence(s) cut, {swapped} chart(s) replaced, {words} words left")
    left = [pr for pr in check_script(script, bundle, min_words=0) if not any(s in pr for s in SOFT)]
    need = (TARGET_WORDS[0] if min_words is None else min_words) * 0.7
    if left or words < need:
        raise ValueError(f"the script cannot be settled ({words} words, need {need:.0f}): {left[:3]}")
    return script


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
    log(f"[plotline] still {len(check_script(script, bundle))} problem(s) after {tries} rewrites; settling by rule")
    return settle(script, bundle, log=log)


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
            title = s["name"] + (f": change since {datasets.when(s, pts[0][0])}" if s.get("index") else "")
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
            spec = {**base, "type": "counter", "label": label[:44], "value": p[1], **_js_fmt(f), "sub": datasets.when(s, p[0]), "source": src}
            if not s.get("index") and p != pts[0]:
                c = datasets.pct(pts[0][1], p[1])
                spec |= {"badge": f"{c:+.0f}% since {pts[0][0][:4]}", "badgeColor": "coral" if c > 0 else "volt"}
            return spec
        a = datasets.at(s["points"], str(v["from"]))
        b = s["points"][-1] if str(v.get("to", "last")) == "last" else datasets.at(s["points"], str(v["to"]))
        if a[0] >= b[0]:
            raise ValueError("compare needs an earlier 'from' and a later 'to'")
        lab = lambda d: d[:4] if s.get("yearly") else datasets.month_name(d)[:3] + " " + d[:4]
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
            items.append({"label": bundle["series"][i].get("label") or _short(bundle["series"][i]["name"]), "value": round(datasets.pct(pts[0][1], pts[-1][1]), 1)})
        items.sort(key=lambda d: -d["value"])
        when = datasets.when(bundle["series"][ids[0]], datasets.window(bundle["series"][ids[0]]["points"], since)[0][0])
        small = max(abs(d["value"]) for d in items) < 10
        srcs = sorted({bundle["series"][i]["source"] for i in ids})
        return {**base, "type": "bars", "title": f"Price change since {when}" if all(bundle["series"][i]["fmt"].get("prefix") == "$" for i in ids)
                else f"Change since {when}", "items": items, "suffix": "%", "prefix": "", "decimals": 1 if small else 0, "highlight": 0,
                "source": srcs[0] if len(srcs) == 1 else "; ".join(s.replace(" via FRED", "") for s in srcs) + " via FRED"}
    if t in NEW_TYPES:
        return _compile_new(t, v, bundle, base)
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


NEW_TYPES = ("multiline", "race", "slope", "kpi", "waffle", "gauge", "donut", "heatmap", "world_map", "stacked", "scatter")
PALETTE_SERIES = 6


def _label(s: dict) -> str:
    return s.get("label") or _short(s["name"])


def _ids(v: dict, bundle: dict, lo: int, hi: int) -> list[str]:
    ids = [i for i in (v.get("series") if isinstance(v.get("series"), list) else [v.get("series")]) if i in bundle["series"]][:hi]
    if len(ids) < lo:
        raise ValueError(f"{v.get('type')} needs {lo} to {hi} of the video's series ids")
    return ids


def _same_unit(ids: list[str], bundle: dict) -> None:
    """Series that can share one axis: no index, and the same kind of number (all dollars, all percents, all counts)."""
    kinds = {(bundle["series"][i]["fmt"].get("prefix", ""), bundle["series"][i]["fmt"].get("suffix", "").strip(),
              bool(bundle["series"][i]["fmt"].get("compact"))) for i in ids}
    if len(kinds) > 1 or any(bundle["series"][i].get("index") for i in ids):
        raise ValueError("these series must be the same kind of number (all dollars, all percents, all counts) and none may be an index")


def _merge_sources(srcs) -> str:
    """Several sources on one line: "A; B via FRED" when all come through FRED, else "A; B"."""
    srcs = sorted(set(srcs))
    if len(srcs) > 1 and all(x.endswith(" via FRED") for x in srcs):
        return "; ".join(x.removesuffix(" via FRED") for x in srcs) + " via FRED"
    return "; ".join(srcs)


def _src(ids: list[str], bundle: dict) -> str:
    return _merge_sources(bundle["series"][i]["source"] for i in ids)


def _compile_new(t: str, v: dict, bundle: dict, base: dict) -> dict:
    S = bundle["series"]
    if t == "multiline":
        ids = _ids(v, bundle, 2, PALETTE_SERIES)
        since, value_mode = str(v.get("since") or bundle["start"]), v.get("as") == "value"
        if value_mode:
            _same_unit(ids, bundle)
        lines, small = [], True
        for i in ids:
            pts = datasets.window(S[i]["points"], since)
            if len(pts) < 2:
                raise ValueError(f"{i} has no data since {since}")
            pts = pts if value_mode else [(d, round(datasets.pct(pts[0][1], x), 1)) for d, x in pts]
            small = small and max(abs(x) for _, x in pts) < 10
            lines.append({"label": _label(S[i]), "points": pts})
        f = _js_fmt(S[ids[0]]["fmt"]) if value_mode else {"prefix": "", "suffix": "%", "decimals": 1 if small else 0, "compact": False}
        when = datasets.when(S[ids[0]], datasets.window(S[ids[0]]["points"], since)[0][0])
        return {**base, "type": "multiline", "title": (S[ids[0]]["name"] + " compared") if value_mode else f"Change since {when}", "lines": lines, **f,
                "source": _src(ids, bundle), "draw": round(min(max(base["duration"] * 0.6, 3), 8), 2)}
    if t == "race":
        ids = _ids(v, bundle, 3, 10)
        _same_unit(ids, bundle)
        since = str(v.get("since") or bundle["start"])
        win = {i: datasets.window(S[i]["points"], since) for i in ids}
        y0, y1 = max(int(w[0][0][:4]) for w in win.values()), min(int(w[-1][0][:4]) for w in win.values())
        if y1 - y0 < 3:
            raise ValueError("race needs at least 4 years of data in common")
        step = max(1, (y1 - y0) // 40)
        years = list(range(y0, y1 + 1, step)) + ([y1] if (y1 - y0) % step else [])
        items = [{"label": _label(S[i]), "values": [datasets.at(win[i], f"{y}-01")[1] for y in years]} for i in ids]
        hi_ = next((k for k, i in enumerate(ids) if _label(S[i]) in ("United States", "United Kingdom")), None)
        return {**base, "type": "race", "title": f"{S[ids[0]]['name'].split(' in ')[0]}: {y0} to {y1}", "frames": [str(y) for y in years], "items": items,
                **_js_fmt(S[ids[0]]["fmt"]), "highlight": hi_, "source": _src(ids, bundle)}
    if t == "slope":
        ids = _ids(v, bundle, 2, 8)
        _same_unit(ids, bundle)
        frm, to = str(v["from"]), str(v.get("to", "last"))
        items, da, db = [], None, None
        for i in ids:
            pts = S[i]["points"]
            a = datasets.at(pts, frm)
            b = pts[-1] if to == "last" else datasets.at(pts, to)
            if a[0] >= b[0]:
                raise ValueError("slope needs an earlier 'from' and a later 'to'")
            da, db = da or a[0], db or b[0]
            items.append({"label": _label(S[i]), "a": a[1], "b": b[1]})
        items.sort(key=lambda d: -d["b"])
        return {**base, "type": "slope", "title": f"{datasets.when(S[ids[0]], da)} vs. {datasets.when(S[ids[0]], db)}", "items": items,
                "aLabel": datasets.when(S[ids[0]], da), "bLabel": datasets.when(S[ids[0]], db), **_js_fmt(S[ids[0]]["fmt"]), "source": _src(ids, bundle)}
    if t == "kpi":
        ids = _ids(v, bundle, 2, 4)
        cards = []
        for i in ids:
            s = S[i]
            pts = datasets.window(s["points"], str(v.get("since") or bundle["start"])) or s["points"]
            c = datasets.pct(pts[0][1], pts[-1][1])
            step = max(1, len(pts) // 40)
            spark = [x for _, x in pts[::step]] + [pts[-1][1]]
            if s.get("index"):
                f, value = {"prefix": "", "suffix": "%", "decimals": 0, "compact": False}, round(c)
                spark = [datasets.pct(pts[0][1], x) for x in spark]
            else:
                f, value = _js_fmt(s["fmt"]), pts[-1][1]
            cards.append({"label": _label(s), "value": value, **f, "valueText": datasets.fmt(value, {**s["fmt"], **({"suffix": "%", "prefix": "", "decimals": 0, "compact": False} if s.get("index") else {})}),
                          "change": f"{c:+.0f}%", "up": c > 0, "since": f"since {datasets.when(s, pts[0][0])}", "spark": spark})
        return {**base, "type": "kpi", "title": "The numbers at a glance", "cards": cards, "source": _src(ids, bundle)}
    if t == "waffle":
        sid = _ids({**v, "series": v.get("series")}, bundle, 1, 1)[0]
        s = S[sid]
        if s["fmt"].get("suffix", "").strip() != "%" or s.get("index"):
            raise ValueError("waffle needs a series measured in percent")
        pts = datasets.window(s["points"], str(v.get("start") or bundle["start"])) or s["points"]
        p = {"last": pts[-1], "max": max(pts, key=lambda q: q[1]), "min": min(pts, key=lambda q: q[1])}[v.get("stat", "last")]
        if not 0 < p[1] <= 100:
            raise ValueError("waffle needs a value between 0 and 100")
        return {**base, "type": "waffle", "label": s["name"][:48], "value": p[1], **_js_fmt(s["fmt"]), "sub": datasets.when(s, p[0]),
                "caption": f"about 1 in {round(100 / p[1])}" if 4 <= p[1] <= 50 else "", "source": s["source"]}
    if t == "gauge":
        sid = _ids({**v, "series": v.get("series")}, bundle, 1, 1)[0]
        s = S[sid]
        if s.get("index"):
            raise ValueError("gauge cannot show an index")
        pts = datasets.window(s["points"], str(v.get("start") or bundle["start"])) or s["points"]
        lo, hi, cur = min(pts, key=lambda q: q[1]), max(pts, key=lambda q: q[1]), pts[-1]
        if hi[1] <= lo[1]:
            raise ValueError("gauge needs a series that moves")
        below = round(100 * sum(1 for _, x in pts if x < cur[1]) / len(pts))
        return {**base, "type": "gauge", "title": s["name"], "value": cur[1], "min": lo[1], "max": hi[1], "minLabel": datasets.when(s, lo[0]), "maxLabel": datasets.when(s, hi[0]),
                "label": f"{s['name']}, {datasets.when(s, cur[0])}", "sub": f"Higher than {below}% of readings since {pts[0][0][:4]}", **_js_fmt(s["fmt"]), "source": s["source"]}
    if t == "donut":
        ids = _ids(v, bundle, 2, 7)
        if len({S[i]["unit"] for i in ids}) > 1 or not all(S[i].get("additive") for i in ids):
            raise ValueError("donut needs series marked additive that share one unit")
        items = sorted(({"label": _label(S[i]).replace(" jobs", ""), "value": S[i]["points"][-1][1]} for i in ids), key=lambda d: -d["value"])
        return {**base, "type": "donut", "title": f"How it splits, {datasets.when(S[ids[0]], S[ids[0]]['points'][-1][0])}", "items": items, "source": _src(ids, bundle)}
    if t == "heatmap":
        sid = _ids({**v, "series": v.get("series")}, bundle, 1, 1)[0]
        s = S[sid]
        if s.get("yearly") or len(s["points"]) < 36:
            raise ValueError("heatmap needs a monthly series with at least three years of data")
        ch = {s["points"][k][0]: datasets.pct(s["points"][k - 1][1], s["points"][k][1]) for k in range(1, len(s["points"]))}
        last_year = int(s["points"][-1][0][:4])
        n = max(3, min(16, int(v.get("years", 8))))
        rows = [{"year": y, "values": [round(ch[f"{y}-{m:02d}-01"], 2) if f"{y}-{m:02d}-01" in ch else None for m in range(1, 13)]} for y in range(last_year - n + 1, last_year + 1)]
        flat = sorted(abs(x) for r in rows for x in r["values"] if x is not None)
        if not flat:
            raise ValueError("no data for the heatmap")
        vmax = max(0.1, round(flat[int(0.95 * (len(flat) - 1))], 1))
        return {**base, "type": "heatmap", "title": f"{s['name']}: monthly change", "rows": rows, "vmax": vmax, "suffix": "%", "prefix": "", "decimals": 1,
                "legend": "monthly change", "source": s["source"]}
    if t == "stacked":
        ids = _ids(v, bundle, 3, 7)
        if len({S[i]["unit"] for i in ids}) > 1 or not all(S[i].get("additive") for i in ids):
            raise ValueError("stacked needs series marked additive that share one unit")
        since = str(v.get("since") or bundle["start"])
        common = sorted(set.intersection(*[{d for d, _ in datasets.window(S[i]["points"], since)} for i in ids]))
        if len(common) < 24:
            raise ValueError("stacked needs at least two years of dates in common")
        step = max(1, len(common) // 150)
        common = common[::step] + ([common[-1]] if (len(common) - 1) % step else [])
        layers = []
        for i in ids:
            val = dict(S[i]["points"])
            layers.append({"label": _label(S[i]).replace(" jobs", ""), "points": [(d, val[d]) for d in common]})
        layers.sort(key=lambda lay: -lay["points"][-1][1])           # the biggest part at the bottom
        share = v.get("as", "share") != "total"
        return {**base, "type": "stacked", "title": ("Share of " if share else "") + S[ids[0]]["unit"].replace("jobs", "jobs by sector") + f", {common[0][:4]} to {common[-1][:4]}",
                "layers": layers, "mode": "share" if share else "total", **_js_fmt(S[ids[0]]["fmt"]), "source": _src(ids, bundle), "draw": round(min(max(base["duration"] * 0.6, 3), 6), 2)}
    if t == "scatter":
        pr = bundle.get("pair")
        if not pr:
            raise ValueError("this video has no second dataset to set against the first (plan needs owid2 or states2)")
        xm, ym = pr["xmeta"], pr["ymeta"]
        keys = list(pr["x"])
        hi = set(pr.get("highlight") or []) if pr["kind"] == "countries" else {k for k, _ in sorted(pr["x"].items(), key=lambda kv: kv[1])[:2]} | {k for k, _ in sorted(pr["x"].items(), key=lambda kv: -kv[1])[:3]}
        pts = [{"label": pr["names"].get(k, k), "x": pr["x"][k], "y": pr["y"][k], "hi": k in hi} for k in keys]
        xs, ys = [p["x"] for p in pts], [p["y"] for p in pts]
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        den = sum((a - mx) ** 2 for a in xs) or 1
        slope = sum((a - mx) * (b - my) for a, b in zip(xs, ys, strict=True)) / den
        xlog = pr["kind"] == "countries" and min(xs) > 0 and max(xs) / min(xs) > 30
        trend = None
        if not xlog:
            x0, x1 = min(xs), max(xs)
            trend = {"x0": x0, "y0": my + slope * (x0 - mx), "x1": x1, "y1": my + slope * (x1 - mx)}
        trails = []
        if v.get("trails") and pr["kind"] == "countries":
            for k in hi:
                path = datasets.pair_path(xm, ym, k, int(bundle["start"]), int(pr["year"]))
                if len(path) >= 4:
                    trails.append({"label": k, "pts": path})
        return {**base, "type": "scatter", "title": f"{xm['name']} and {ym['name']}", "points": pts, "trails": trails, "xlog": xlog, "trend": trend,
                "xLabel": xm["name"], "yLabel": ym["name"], "xfmt": _js_fmt(xm["fmt"]), "yfmt": _js_fmt(ym["fmt"]),
                "note": f"correlation {datasets.correlation(xs, ys):+.2f}", "source": _merge_sources([xm["source"], ym["source"]])}
    if t == "world_map":
        ow = bundle["owid"]
        if not ow:
            raise ValueError("this video has no country data")
        values, year = datasets.world_values(ow)
        if len(values) < 40:
            raise ValueError("not enough countries for a world map")
        want = datasets.WORLD_ALIASES.get(str(v.get("highlight") or ""), str(v.get("highlight") or ""))
        top = want if want in values else max(values, key=values.get)
        return {**base, "type": "world_map", "title": f"{ow['name']}, {year}", "values": values, **_js_fmt(ow["fmt"]), "legend": f"{ow['name']}, {year}", "highlight": top,
                "highlightName": top.replace("United States of America", "United States"), "source": ow["source"]}
    raise ValueError(f"unknown chart type {t!r}")


def shown_numbers(spec: dict) -> set[float]:
    """The headline numbers a chart displays (rounded as on screen), to check them against the narration."""
    f = {"prefix": spec.get("prefix", ""), "suffix": spec.get("suffix", ""), "decimals": spec.get("decimals", 0), "compact": spec.get("compact")}
    vals = []
    if spec["type"] in ("waffle", "gauge"):
        vals = [spec["value"]] + ([spec["min"], spec["max"]] if spec["type"] == "gauge" else [])
    elif spec["type"] == "counter":
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
        if "value" in item:
            item["value"] = float(f"{item['value']:.{d}f}")
    return spec


def _js_fmt(f: dict) -> dict:
    return {"prefix": f.get("prefix", ""), "suffix": f.get("suffix", ""), "decimals": f.get("decimals", 0), "compact": bool(f.get("compact"))}


# ---- 4. video -----------------------------------------------------------------------------------------------------------
def make_video(script: dict, bundle: dict, out_dir: Path, log=print) -> Path:
    from autopilot import render, tts

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
    beat = make_bed(total + 2, out_dir / "music.wav", seed=len(script["title"]), mood=bundle_mood(bundle))
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
# A real YouTube thumbnail: a bold photo of the subject, the striking number huge in lime, a red label, a few words in
# heavy white type, and the data's own line rising across the picture.
THUMB = """<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: "Space Grotesk"; src: url("{stage}/fonts/SpaceGrotesk.ttf"); font-weight: 300 700; }}
@font-face {{ font-family: "Inter"; src: url("{stage}/fonts/Inter.ttf"); font-weight: 100 900; }}
html, body {{ margin: 0; width: 1280px; height: 720px; overflow: hidden; background: #0b0d17; }}
.photo {{ position: absolute; inset: 0 0 0 330px; background: url("{photo}") center/cover; filter: saturate(1.45) contrast(1.15) brightness(1.02) sepia(.12); }}
.shade {{ position: absolute; inset: 0; background: linear-gradient(90deg, #0b0d17 0%, #0b0d17 30%, rgba(11,13,23,.82) 44%, rgba(11,13,23,.15) 70%, rgba(11,13,23,0) 100%),
          linear-gradient(0deg, rgba(11,13,23,.85) 0%, rgba(11,13,23,0) 38%); }}
.glow {{ position: absolute; left: -120px; top: -160px; width: 760px; height: 760px; background: radial-gradient(circle, rgba(57,210,255,.28), transparent 65%); }}
svg {{ position: absolute; inset: 0; }}
.label {{ position: absolute; left: 58px; top: 52px; background: #ff3b5c; color: #fff; font: 700 44px "Space Grotesk"; letter-spacing: 1px;
          padding: 6px 22px 10px; border-radius: 14px; transform: rotate(-4deg); box-shadow: 0 10px 30px rgba(255,59,92,.45); }}
.num {{ position: absolute; left: 44px; top: 118px; font: 700 {nsize}px/1 "Space Grotesk"; color: #d4ff3a; letter-spacing: -6px;
        -webkit-text-stroke: 12px #0b0d17; paint-order: stroke fill; transform: rotate(-3deg);
        text-shadow: 0 0 40px rgba(212,255,58,.55), 0 14px 0 #0b0d17; }}
.words {{ position: absolute; left: 58px; top: {wtop}px; width: 640px; font: 700 {wsize}px/1.02 "Space Grotesk"; color: #fff; text-transform: uppercase;
          -webkit-text-stroke: 10px #0b0d17; paint-order: stroke fill; text-shadow: 0 8px 24px rgba(0,0,0,.6); }}
.arrow {{ font: 700 0.42em/1 "Inter"; color: {acolor}; -webkit-text-stroke: 7px #0b0d17; paint-order: stroke fill; letter-spacing: 0;
          vertical-align: 0.95em; margin-left: 14px; text-shadow: 0 0 30px {acolor}; }}
</style></head><body>
<div class="photo"></div><div class="shade"></div><div class="glow"></div>
<svg width="1280" height="720"><defs>
 <filter id="g" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
 <linearGradient id="f" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d4ff3a" stop-opacity=".40"/><stop offset="1" stop-color="#d4ff3a" stop-opacity="0"/></linearGradient></defs>
 <path d="{area}" fill="url(#f)"/>
 <path d="{line}" fill="none" stroke="#0b0d17" stroke-width="26" stroke-linejoin="round" stroke-linecap="round" opacity=".7"/>
 <path d="{line}" fill="none" stroke="#d4ff3a" stroke-width="13" stroke-linejoin="round" stroke-linecap="round" filter="url(#g)"/>
 <circle cx="{px}" cy="{py}" r="34" fill="none" stroke="#d4ff3a" stroke-width="6" opacity=".7"/>
 <circle cx="{px}" cy="{py}" r="20" fill="#fff" filter="url(#g)"/>
</svg>
<div class="label">{label}</div><div class="num">{number}<span class="arrow">{arrow}</span></div><div class="words">{words}</div>
</body></html>"""

THUMB_PROMPT = """For a YouTube thumbnail of the data video "{title}" (striking number: {number}), return JSON {{"label": str (2 words, ALL
CAPS, e.g. "RECORD HIGH", "ALL-TIME LOW", "UP 133%"; must be true for the number), "words": str (2 to 4 punchy words, e.g. "WHY EGGS EXPLODED"),
"photo": str (a 1 to 3 word stock-photo search for a concrete, recognisable object, e.g. "egg carton", "gas pump", "house keys"),
"direction": "up" or "down" (did the number rise or fall)}}"""


def thumb_photo(query: str, cache: Path, gen=None) -> Path | None:
    """The most fitting Pixabay photo for `query`: a vision model picks from the top results (keyword search alone returns
    Easter eggs for "eggs"); the first result is the fallback."""
    from autopilot import stock

    try:
        hits = stock.search_photos(query)[:6]
    except (OSError, ValueError):
        return None
    if not hits:
        return None
    pick = 0
    try:
        thumbs = [stock._fetch(h["thumb"], cache / f"pixthumb_{h['id']}.jpg").read_bytes() for h in hits]
        ans = (gen or llm.generate_json)(f"These {len(thumbs)} photos are candidates for a YouTube thumbnail about \"{query}\". Which one shows "
                                         f"{query} most plainly and boldly, with warm, rich colour (real, ordinary, well lit, close up, nothing seasonal or decorative, not grey or washed out)? Return JSON "
                                         "{\"index\": number from 0}", images=thumbs)
        pick = max(0, min(len(hits) - 1, int(ans.get("index", 0))))
    except (llm.LLMError, OSError, ValueError, TypeError):
        pass
    return stock.download_photo(hits[pick], cache)


def make_thumbnail(script: dict, bundle: dict, out: Path, gen=None) -> Path:
    from html import escape

    gen = gen or llm.generate_json
    th = dict(script.get("thumbnail") or {})
    number = str(th.get("number") or "")
    if not all(th.get(k) for k in ("label", "photo", "direction")):
        try:
            th |= {k: v for k, v in gen(THUMB_PROMPT.format(title=script["title"], number=number)).items() if v}
        except llm.LLMError:
            pass
    s = next(iter(bundle["series"].values()), None)
    pts = [v for _, v in datasets.window(s["points"], bundle["start"])] if s else [1, 2, 1.5, 3, 2.5, 4]
    step = max(1, len(pts) // 90)
    pts = pts[::step] + [pts[-1]]
    lo, hi = min(pts), max(pts)
    xy = [(470 + 760 * i / (len(pts) - 1), 690 - 330 * ((v - lo) / ((hi - lo) or 1))) for i, v in enumerate(pts)]
    line = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in xy)
    area = line + f" L{xy[-1][0]:.1f},720 L{xy[0][0]:.1f},720 Z"
    photo = thumb_photo(str(th.get("photo") or ""), out.parent / "photos", gen) if th.get("photo") else None
    words = str(th.get("words") or script["title"]).upper()
    up = str(th.get("direction", "up")).lower() != "down"
    nsize = 250 if len(number) <= 5 else 210 if len(number) <= 7 else 170
    html = THUMB.format(stage=motion.STAGE.as_uri(), photo=photo.resolve().as_uri() if photo else "", area=area, line=line, px=xy[-1][0],
                        py=xy[-1][1], number=escape(number), nsize=nsize, label=escape(str(th.get("label") or "THE DATA").upper()),
                        words=escape(words), wsize=86 if len(words) <= 16 else 72, wtop=118 + nsize + 30,
                        arrow="▲" if up else "▼", acolor="#ff3b5c" if up else "#39d2ff")
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".html")
    tmp.write_text(html)
    with motion.Browser() as b:
        page = b._b.new_page(viewport={"width": 1280, "height": 720})
        page.goto(tmp.resolve().as_uri())
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(300)
        page.screenshot(path=str(out), type="jpeg", quality=92)
    tmp.unlink()
    return out


# ---- Shorts -------------------------------------------------------------------------------------------------------------
SHORT_FRAME = {"canvas": [1080, 1920], "width": 1080, "height": 1350, "offset": 200}   # chart area; captions sit below it
SHORT_CAPTIONS = {"res": (1080, 1920), "font": 74, "margin_v": 150, "group": 3, "upper": True, "outline": 6, "fontname": "Lato"}
SHORT_WORDS = (70, 110)

SHORTS_PROMPT = """From this Plotline Data video, "{title}", write {n} YouTube Shorts (vertical, 30 to 45 seconds each) for US and UK
viewers. Each Short tells ONE surprising number from the video in a self-contained way: a hook in the first sentence (a question or
a shocking number), 2 to 3 quick beats, and a last line pointing to the full video ("The full story is on the channel.").
Each Short uses a different number and a different angle. Titles already used (do not repeat them): {avoid}.

FACTS (the ONLY numbers you may say; never invent a number):
{facts}

The full video's narration, for reference:
{story}

Each Short: {wmin} to {wmax} words, 4 to 6 scenes of 1 to 2 short sentences, each scene with one chart that SHOWS the number it says.
Write numbers as digits ($6.23, 4.5%, 2020). No politics, no financial advice.

{visuals}

Data ids you may use: {ids}

Return JSON {{"shorts": [{{"title": str (max 60 chars, punchy, no hashtags), "scenes": [{{"narration": str, "visual": {{...}}}}]}}]}}"""


def write_shorts(script: dict, bundle: dict, n: int = 3, gen=None, log=print) -> list[dict]:
    """n Shorts. A Short that cannot be repaired by rewrites is settled by rule; if some still fail, more are asked for (twice)."""
    gen = gen or llm.generate_json
    ids = list(bundle["series"]) + (["state data"] if bundle["states"] else []) + (["country data"] if bundle["owid"] else [])
    facts = "\n".join(bundle["facts"])
    story = " ".join(s["narration"] for s in script["scenes"])[:6000]
    shorts: list[dict] = []
    for _ in range(3):
        want = n - len(shorts)
        if want <= 0:
            break
        avoid = "; ".join(s["title"] for s in shorts) or "none"
        out = gen(SHORTS_PROMPT.format(title=script["title"], n=want, facts=facts, story=story, wmin=SHORT_WORDS[0], wmax=SHORT_WORDS[1],
                                       visuals=VISUALS, ids=", ".join(ids), avoid=avoid))
        for sh in (out.get("shorts") or [])[:want]:
            sh["scenes"] = [s for s in sh.get("scenes") or [] if s.get("narration") and isinstance(s.get("visual"), dict)]
            if not sh["scenes"]:
                continue
            sh["scenes"][0]["visual"] = {"type": "title", "text": sh.get("title") or script["title"], "highlight": []}
            try:
                shorts.append(_fix_short(sh, plan_title=script["title"], bundle=bundle, facts=facts, ids=ids, gen=gen, log=log))
            except ValueError as exc:
                log(f"[plotline] a Short was dropped: {exc}")
    return shorts


def _fix_short(sh: dict, plan_title: str, bundle: dict, facts: str, ids: list[str], gen, log, tries: int = 2) -> dict:
    for attempt in range(tries + 1):
        problems = [p for p in check_script(sh, bundle, min_words=0) if not any(s in p for s in SOFT)]
        if not problems:
            return sh
        if attempt == tries:
            break
        log(f"[plotline] Short '{sh.get('title')}' check {attempt + 1}: {problems[:3]}")
        for pr in problems:
            if m := re.match(r"scene (\d+): (.*)", pr):
                k = int(m.group(1)) - 1
                try:
                    new = gen(FIX_PROMPT.format(title=plan_title, before=json.dumps(sh["scenes"][k - 1]) if k else "(none)",
                                                scene=json.dumps(sh["scenes"][k]), after=json.dumps(sh["scenes"][k + 1]) if k + 1 < len(sh["scenes"]) else "(none)",
                                                problems=m.group(2), facts=facts, visuals=VISUALS, ids=", ".join(ids)))
                except llm.LLMError:
                    continue
                if new.get("narration") and isinstance(new.get("visual"), dict):
                    sh["scenes"][k] = {"narration": new["narration"], "visual": new["visual"]}
    return settle(sh, bundle, min_words=SHORT_WORDS[0] * 0.6, log=log)


def make_short(short: dict, bundle: dict, out_dir: Path, log=print) -> Path:
    """A vertical Short: charts in the upper area, word-by-word captions below, voice and music."""
    from autopilot import render, tts

    out_dir.mkdir(parents=True, exist_ok=True)
    narration, timings_path = out_dir / "narration.wav", out_dir / "timings.json"
    if not timings_path.exists():
        timings = tts.synthesize_script({"sections": [{"heading": f"scene {i + 1}", "narration": s["narration"]}
                                                      for i, s in enumerate(short["scenes"])]}, narration, tts.build_engine(VOICE))
        timings_path.write_text(json.dumps(timings))
    timings = json.loads(timings_path.read_text())
    total = timings[-1]["end"] + 1.0
    specs = []
    for i, sc in enumerate(short["scenes"]):
        start = 0.0 if i == 0 else timings[i]["start"]
        end = timings[i + 1]["start"] if i + 1 < len(timings) else total
        spec = compile_visual(sc["visual"], bundle, end - start)
        if spec["type"] == "map":                           # a map is too small in a vertical frame: show the ranking instead
            spec = compile_visual({"type": "states_bars", "order": "top", "n": 8}, bundle, end - start)
        specs.append({**spec, **SHORT_FRAME})
    files = render_cached(specs, out_dir.parent / "scenes")
    listing = out_dir / "scenes.txt"
    listing.write_text("".join(f"file '{p.resolve()}'\n" for p in files))
    charts = out_dir / "charts.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(charts)], check=True)
    ass = out_dir / "captions.ass"
    render.write_ass_words(timings, ass, SHORT_CAPTIONS)
    beat = make_bed(total + 2, out_dir / "music.wav", seed=len(short.get("title", "")), mood=bundle_mood(bundle))
    mixed = out_dir / "mix.wav"
    log(f"[mix] Short audio: {render.mix_audio(narration, beat, mixed)}")
    final = out_dir / "final.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(charts), "-i", str(mixed), "-filter_complex", f"[0:v]ass={ass}[v];[1:a]apad[a]",
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac",
                    "-b:a", "160k", "-t", f"{min(total, 59.5):.3f}", str(final)], check=True)
    return final
