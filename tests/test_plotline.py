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
