from autopilot import retention as rt


def curve(f, n=100):
    return [(0.0, 1.0)] + [((i + 1) / n, f((i + 1) / n)) for i in range(n)]


def test_hook_leak_and_the_steepest_cliff_are_found_and_mapped_to_the_section():
    # 100% -> 70% over the first 5% (a leaking hook), a slow slide, then a sharp 12-point cliff at 50%
    def f(x):
        base = 1.0 - 0.3 * min(1.0, x / 0.05) - 0.15 * x
        return base - (0.12 if x > 0.5 else 0)
    vmap = {"segments": [{"start": 0, "end": 300, "label": "intro", "text": "alpha " * 100}, {"start": 300, "end": 600, "label": "dense maths", "text": "beta " * 100}]}
    found = rt.analyse(curve(f), 600, vmap)
    assert found["hook"] in ("leaking", "severe") and found["hook_leak_pp"] > 25
    top = found["cliffs"][0]
    assert 290 <= top["at_s"] <= 310 or top["at_s"] < 40          # the cliff at the half or the hook itself
    assert any(c["section"] == "dense maths" for c in found["cliffs"]) or any(c["section"] == "intro" for c in found["cliffs"])
    text = rt.render("T", found, 120)
    assert "T (120 views)" in text and "hook:" in text and "drop" in text


def test_a_flat_healthy_curve_and_too_little_data_are_reported_plainly():
    ok = rt.analyse(curve(lambda x: 1.0 - 0.25 * x), 420)
    assert ok["hook"] == "healthy" and ok["cliffs"] == []
    assert rt.analyse([(0.1, 1.0), (0.5, 0.5)], 420) == {"error": "not enough retention data yet"}
    assert "not enough" in rt.render("T", rt.analyse([], 100))


def test_replayed_moments_show_as_rises_with_the_words_near_them():
    def f(x):
        return 1.0 - 0.3 * x + (0.05 if 0.6 < x < 0.7 else 0)
    vmap = rt.estimate_map("long", "t", [("a", "one two three four five six seven eight nine ten " * 10)] * 2, 300)
    found = rt.analyse(curve(f), 300, vmap)
    assert found["rewatched"] and 170 <= found["rewatched"][0]["at_s"] <= 190 and found["rewatched"][0]["said"]


def test_maps_from_timings_and_estimates_cover_the_whole_video():
    timings = [{"heading": "A", "start": 0.0, "end": 5.0, "sentences": [{"text": "Hello there.", "start": 0.0, "end": 2.0}, {"text": "More.", "start": 2.0, "end": 5.0}]},
               {"heading": "B", "start": 5.0, "end": 9.0, "sentences": [{"text": "Bye.", "start": 5.0, "end": 9.0}]}]
    long = rt.video_map("long", "t", timings)
    assert [s["label"] for s in long["segments"]] == ["A", "B"] and long["segments"][0]["text"] == "Hello there. More."
    short = rt.video_map("short", "t", timings[:1])
    assert [s["text"] for s in short["segments"]] == ["Hello there.", "More."]
    est = rt.estimate_map("long", "t", [("x", "a b c d"), ("y", "e f")], 60)
    assert est["segments"][0]["end"] == est["segments"][1]["start"] == 40.0 and est["estimated"]
    assert rt.segment_at(est, 59.9)["label"] == "y" and rt.segment_at(est, 61)["label"] == "y"


def test_shorts_get_wider_bands_and_small_samples_are_flagged():
    c = curve(lambda x: 1.0 - 0.9 * min(1.0, x / 0.25))
    assert rt.analyse(c, 40)["hook"] == "severe"
    leak = rt.analyse(c, 40, short=True)["hook_leak_pp"]
    assert rt.analyse(curve(lambda x: 1.0 - 0.45 * min(1.0, x / 0.25)), 40, short=True)["hook"] == "leaking" and leak > 60
    assert "small sample" in rt.render("T", rt.analyse(c, 40), views=73)
    assert "small sample" not in rt.render("T", rt.analyse(c, 40), views=500)
