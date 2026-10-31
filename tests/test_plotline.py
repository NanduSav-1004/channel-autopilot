from autopilot import datasets, plotline


def _series(index=False):
    pts = [(f"{y}-{m:02d}-01", 1.0 + (y - 2000) * 0.1 + m * 0.001) for y in range(2000, 2026) for m in range(1, 13)]
    return {"id": "X", "name": "Price of a dozen eggs", "unit": "US dollars per dozen", "source": "FRED", "theme": "food",
            "fmt": {"prefix": "$", "decimals": 2}, "index": index, "points": pts}


def _bundle(index=False):
    s = _series(index)
    return {"start": "2000", "series": {"X": s}, "states": None, "owid": None, "facts": [f"[X] {f}" for f in datasets.facts(s, "2000")]}


def test_fmt_compact_and_plain():
    assert datasets.fmt(158_600_000, {"decimals": 1, "compact": True}) == "158.6 million"
    assert datasets.fmt(36.2e12, {"prefix": "$", "decimals": 1, "compact": True}) == "$36.2 trillion"
    assert datasets.fmt(6.234, {"prefix": "$", "decimals": 2}) == "$6.23"


def test_monthly_averages_daily_data_but_keeps_monthly():
    daily = [("2020-01-01", 1.0), ("2020-01-02", 3.0), ("2020-02-01", 5.0)]
    assert datasets.monthly(daily) == [("2020-01-01", 2.0), ("2020-02-01", 5.0)]
    monthly = [("2020-01-01", 1.0), ("2020-02-01", 2.0)]
    assert datasets.monthly(monthly) == monthly


def test_facts_quote_values_and_index_facts_only_changes():
    f = datasets.facts(_series(), "2000")
    assert any(x.startswith("Latest value") for x in f) and any("Highest" in x for x in f)
    fi = datasets.facts(_series(index=True), "2000")
    assert not any(x.startswith("Latest value") for x in fi) and any("percent changes" in x for x in fi)


def test_check_script_flags_invented_numbers_but_allows_roundings_years_and_small_counts():
    b = _bundle()
    last = b["series"]["X"]["points"][-1][1]
    good = {"scenes": [{"narration": f"Eggs cost ${last:.2f} in 2025, over ${int(last)} for 3 years.", "visual": {"type": "counter", "series": "X"}}]}
    assert not [p for p in plotline.check_script(good, b) if "not in the facts" in p]
    bad = {"scenes": [{"narration": "Eggs cost $9.87 now.", "visual": {"type": "counter", "series": "X"}}]}
    assert any("9.87" in p for p in plotline.check_script(bad, b))


def test_check_script_rejects_charts_without_data():
    b = _bundle()
    script = {"scenes": [{"narration": "Look at the map.", "visual": {"type": "map"}},
                         {"narration": "Compare.", "visual": {"type": "bars", "series": ["X"]}}]}
    problems = plotline.check_script(script, b)
    assert any("scene 1: bad visual" in p for p in problems) and any("scene 2: bad visual" in p for p in problems)


def test_charts_are_built_from_the_data_not_the_request():
    b = _bundle()
    spec = plotline.compile_visual({"type": "counter", "series": "X", "stat": "max"}, b, 5.0)
    assert spec["value"] == round(max(v for _, v in b["series"]["X"]["points"]), 2) and spec["prefix"] == "$"   # rounded as shown
    line = plotline.compile_visual({"type": "line", "series": "X", "start": "2010", "annotate": ["max"]}, b, 10.0)
    assert line["series"][0][0].startswith("2010") and line["annotations"][0]["label"].startswith("Peak: $")


def test_an_index_is_shown_as_percent_change_and_cannot_be_compared():
    b = _bundle(index=True)
    line = plotline.compile_visual({"type": "line", "series": "X", "start": "2000"}, b, 8.0)
    assert line["series"][0][1] == 0 and line["suffix"] == "%"
    assert any("bad visual" in p for p in plotline.check_script(
        {"scenes": [{"narration": "x", "visual": {"type": "compare", "series": "X", "from": "2000"}}]}, b))


def test_daily_run_skips_a_finished_day(tmp_path, monkeypatch):
    import json
    from datetime import datetime, timezone

    from autopilot import plotline_daily

    monkeypatch.setattr(plotline_daily, "STATE", tmp_path)
    day = {"title": "T", "video_id": "abc", "shorts": [{"video_id": f"s{i}"} for i in range(plotline_daily.SHORTS_PER_DAY)]}
    (tmp_path / "state.json").write_text(json.dumps({"days": {"2026-11-01": day}}))
    msg = plotline_daily.run(live=True, privacy="public", now=datetime(2026, 11, 1, 5, tzinfo=timezone.utc))
    assert "nothing to do" in msg


def test_description_lists_sources_and_disclosure():
    from autopilot import plotline_daily

    b = _bundle()
    text = plotline_daily.description({"description": "About eggs."}, b, long_id="xyz")
    assert "About eggs." in text and "youtu.be/xyz" in text and "- FRED" in text and "synthetic voice" in text


def test_thumbnail_works_with_a_relative_output_path(tmp_path, monkeypatch):
    # the workflow writes to output/plotline/<day>/thumbnail.jpg: a RELATIVE path, which once crashed the browser's file URL
    monkeypatch.chdir(tmp_path)
    b = _bundle()
    script = {"title": "Eggs", "thumbnail": {"number": "$6.23", "words": "Why prices exploded", "label": "RECORD HIGH", "photo": "", "direction": "up"}}
    out = plotline.make_thumbnail(script, b, __import__("pathlib").Path("output/plotline/2026-11-01/thumbnail.jpg"))
    assert out.exists() and out.stat().st_size > 10_000


def _long_script(b, extra_scenes=()):
    last = b["series"]["X"]["points"][-1][1]
    ok = {"narration": f"Eggs cost ${last:.2f} now. " + "This is a filler sentence about the long view of the data. " * 6,
          "visual": {"type": "line", "series": "X", "start": "2000"}}
    return {"title": "Eggs", "scenes": [ok] * 60 + list(extra_scenes)}


def test_settle_repairs_by_rule_instead_of_losing_the_video():
    b = _bundle()
    bad = [
        {"narration": "Prices jumped 987.65 percent. Eggs are a staple.", "visual": {"type": "line", "series": "X"}},   # invented number
        {"narration": "It cost $4.00 once.", "visual": {"type": "counter", "series": "X", "stat": "max"}},              # chart shows another number
        {"narration": "Look at the map of states.", "visual": {"type": "map"}},                                         # no state data
        {"narration": "Only 987.65 here.", "visual": {"type": "line", "series": "X"}},                                  # nothing left: dropped
    ]
    script = plotline.settle(_long_script(b, bad), b, log=lambda m: None)
    texts = [s["narration"] for s in script["scenes"]]
    assert not any("987.65" in t for t in texts) and any(t == "Eggs are a staple." for t in texts)
    assert not [p for p in plotline.check_script(script, b, min_words=0) if not any(s in p for s in plotline.SOFT)]
    assert script["scenes"][0]["visual"]["type"] == "title"
    assert all(s["visual"]["type"] != "map" for s in script["scenes"])


def test_settle_refuses_a_script_that_is_too_short_to_be_a_video():
    import pytest

    b = _bundle()
    with pytest.raises(ValueError):
        plotline.settle({"title": "Eggs", "scenes": [{"narration": "Short.", "visual": {"type": "line", "series": "X"}}]}, b, log=lambda m: None)


def test_fix_script_settles_when_the_model_cannot_fix_a_scene():
    b = _bundle()
    stubborn = {"narration": "It cost $4.00 once.", "visual": {"type": "counter", "series": "X", "stat": "max"}}
    script = _long_script(b, [stubborn])
    out = plotline.fix_script(script, {"title": "Eggs"}, b, "facts", ["X"], gen=lambda prompt: dict(stubborn), tries=2, log=lambda m: None)
    assert not [p for p in plotline.check_script(out, b, min_words=0) if not any(s in p for s in plotline.SOFT)]


def test_shorts_are_filled_up_to_the_requested_number():
    b = _bundle()
    last = b["series"]["X"]["points"][-1][1]
    mk = lambda i: {"title": f"Short {i}", "scenes": [{"narration": f"Eggs cost ${last:.2f}. " * 12, "visual": {"type": "counter", "series": "X", "stat": "last"}}]}
    calls = []

    def gen(prompt):
        calls.append(prompt)
        return {"shorts": [mk(len(calls))] if len(calls) < 3 else [mk(3), mk(4)]}      # one short per answer at first

    out = plotline.write_shorts({"title": "Eggs", "scenes": [{"narration": "x", "visual": {}}]}, b, 3, gen=gen, log=lambda m: None)
    assert len(out) == 3 and len(calls) == 3


def test_country_data_becomes_ordinary_series(monkeypatch):
    rows = {"United States": [(2000, 1888.0), (2010, 1773.0), (2023, 1789.0)], "Germany": [(2000, 1452.0), (2023, 1343.0)]}
    monkeypatch.setattr(datasets, "owid", lambda slug: {"slug": slug, "name": "Hours worked per worker per year", "unit": "hours per year",
                                                        "fmt": {"decimals": 0}, "theme": "jobs", "source": "Our World in Data", "rows": rows})
    b = plotline.gather({"title": "t", "series": [], "states": None, "owid": "annual-working-hours-per-worker",
                         "countries": ["United States", "Germany", "Nowhere"], "start": "2000"})
    assert list(b["series"]) == ["united-states", "germany"]
    counter = plotline.compile_visual({"type": "counter", "series": "germany", "stat": "at", "date": "2023"}, b, 4.0)
    assert counter["value"] == 1343.0 and counter["sub"] == "2023"                     # a year, not "January 2023"
    bars = plotline.compile_visual({"type": "bars", "series": ["united-states", "germany"], "since": "2000"}, b, 4.0)
    assert {i["label"] for i in bars["items"]} == {"United States", "Germany"}
    line = plotline.compile_visual({"type": "line", "series": "united-states", "start": "2000"}, b, 6.0)
    assert line["series"][0][0] == "2000-01-01"


def test_the_same_chart_may_not_appear_more_than_twice():
    b = _bundle()
    same = {"narration": "Eggs cost a lot.", "visual": {"type": "line", "series": "X", "start": "2000"}}
    other = {"narration": "Eggs cost a lot.", "visual": {"type": "line", "series": "X", "start": "2010"}}
    problems = plotline.check_script({"scenes": [same, other, same, same]}, b, min_words=0)
    assert any("scene 4: the same chart" in p for p in problems) and not any("scene 3: the same chart" in p for p in problems)


def test_a_refused_thumbnail_is_retried_on_a_later_run(tmp_path, monkeypatch):
    import json

    from autopilot import plotline_daily, upload

    monkeypatch.setattr(plotline_daily, "STATE", tmp_path)
    (tmp_path / "2026-11-01").mkdir()
    (tmp_path / "2026-11-01" / "thumbnail.jpg").write_bytes(b"jpg")
    state = {"days": {"2026-11-01": {"video_id": "abc"}}}
    calls = []

    def refuse(video_id, path, profile="en"):
        calls.append(video_id)
        raise OSError("forbidden")

    monkeypatch.setattr(upload, "set_thumbnail", refuse)
    plotline_daily.retry_thumbnails(state, live=True)
    assert calls == ["abc"] and not state["days"]["2026-11-01"].get("thumbnail_set")
    monkeypatch.setattr(upload, "set_thumbnail", lambda video_id, path, profile="en": calls.append("ok"))
    plotline_daily.retry_thumbnails(state, live=True)
    assert state["days"]["2026-11-01"]["thumbnail_set"] is True
    assert json.loads((tmp_path / "state.json").read_text())["days"]["2026-11-01"]["thumbnail_set"]


def _line_scene(start):
    return {"narration": "Eggs cost a lot.", "visual": {"type": "line", "series": "X", "start": str(start)}}


def test_striking_chart_types_are_limited_to_twice_a_video():
    b = _bundle()
    gauge = {"narration": "Where it stands.", "visual": {"type": "gauge", "series": "X", "start": "2000"}}
    scenes = [_line_scene(2000 + i) for i in range(10)] + [gauge, {**gauge, "visual": {**gauge["visual"], "start": "2005"}}, {**gauge, "visual": {**gauge["visual"], "start": "2010"}}]
    problems = plotline.check_script({"scenes": scenes}, b, min_words=0)
    assert any("chart type 'gauge' is already used 2 times" in p for p in problems)


def test_every_new_chart_type_compiles_from_real_shaped_data():
    b = _bundle()
    jobs = {"id": "J", "name": "Retail jobs", "unit": "jobs", "source": "FRED", "theme": "jobs", "fmt": {"decimals": 1, "compact": True}, "additive": True,
            "points": [(f"{y}-{m:02d}-01", 100.0 + y - 2000 + m) for y in range(2000, 2026) for m in range(1, 13)]}
    jobs2 = {**jobs, "id": "K", "name": "Government jobs"}
    rate = {**_series(), "id": "R", "name": "Saving rate", "unit": "percent", "fmt": {"suffix": "%", "decimals": 1}, "index": False,
            "points": [(f"{y}-{m:02d}-01", 3.0 + (y % 5) + m / 20) for y in range(2000, 2026) for m in range(1, 13)]}
    b["series"] |= {"J": jobs, "K": jobs2, "R": rate}
    for v in ({"type": "multiline", "series": ["J", "K"], "since": "2000"}, {"type": "slope", "series": ["J", "K"], "from": "2000"},
              {"type": "race", "series": ["J", "K", "X"][:2] + ["X"], "since": "2000"}, {"type": "kpi", "series": ["J", "R"]},
              {"type": "waffle", "series": "R"}, {"type": "gauge", "series": "R", "start": "2000"}, {"type": "donut", "series": ["J", "K"]},
              {"type": "heatmap", "series": "J", "years": 5}):
        try:
            spec = plotline.compile_visual(v, b, 6.0)
        except ValueError as exc:                                  # race needs one kind of number: X is dollars, J is a count
            assert v["type"] == "race" and "same kind" in str(exc)
            continue
        assert spec["type"] == v["type"] and spec["duration"] == 6.0


def test_sources_are_merged_without_naming_fred_twice():
    assert plotline._merge_sources(["U.S. Census Bureau via FRED", "U.S. Bureau of Labor Statistics via FRED"]) == \
        "U.S. Bureau of Labor Statistics; U.S. Census Bureau via FRED"
    assert plotline._merge_sources(["Our World in Data", "Our World in Data"]) == "Our World in Data"


def test_scatter_and_stacked_compile_and_need_their_data():
    import pytest

    b = _bundle()
    with pytest.raises(ValueError):
        plotline.compile_visual({"type": "scatter"}, b, 6.0)            # no second dataset in this video
    pts = [(f"{y}-{m:02d}-01", 100.0 + y - 2000 + m) for y in range(2000, 2026) for m in range(1, 13)]
    mk = lambda i, n: {"id": i, "name": n, "unit": "jobs", "source": "FRED", "theme": "jobs", "fmt": {"decimals": 1, "compact": True}, "additive": True, "points": pts}  # noqa: E731
    b["series"] |= {"A": mk("A", "A jobs"), "B": mk("B", "B jobs"), "C": mk("C", "C jobs")}
    spec = plotline.compile_visual({"type": "stacked", "series": ["A", "B", "C"], "as": "share"}, b, 6.0)
    assert spec["type"] == "stacked" and len(spec["layers"]) == 3 and spec["mode"] == "share"
    b["pair"] = {"kind": "countries", "names": {c: c for c in "abcde"}, "x": dict(zip("abcde", [1.0, 2, 3, 4, 5], strict=True)),
                 "y": dict(zip("abcde", [2.0, 4, 5, 8, 10], strict=True)), "year": "2023", "highlight": ["a", "e"],
                 "xmeta": {"name": "GDP", "fmt": {"decimals": 0}, "source": "Our World in Data", "rows": {}},
                 "ymeta": {"name": "Life", "fmt": {"decimals": 1}, "source": "Our World in Data", "rows": {}}}
    sc = plotline.compile_visual({"type": "scatter"}, b, 6.0)
    assert len(sc["points"]) == 5 and sum(p["hi"] for p in sc["points"]) == 2 and sc["note"].startswith("correlation +0.")
