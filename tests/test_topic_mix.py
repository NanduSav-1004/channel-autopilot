import json

from autopilot import db, nasa, topics


def _conn(tmp_path, cats):
    conn = db.connect(tmp_path / "x.db")
    for c in cats:
        db.add_job(conn, f"t{len(cats)}{c}{id(c)}", "long", category=c)
    return conn


MIX = {"core": 0.5, "space": 0.2, "what_if": 0.15, "history": 0.15}


def test_the_least_served_category_goes_next_and_the_shares_follow_the_mix(tmp_path):
    conn = db.connect(tmp_path / "x.db")
    chosen = []
    for _ in range(40):
        cat = topics.pick_category(conn, MIX)
        chosen.append(cat)
        db.add_job(conn, f"topic {len(chosen)}", "long", category=cat)
    share = {k: chosen.count(k) / len(chosen) for k in MIX}
    assert abs(share["core"] - 0.5) < 0.12 and abs(share["space"] - 0.2) < 0.1
    assert share["what_if"] > 0 and share["history"] > 0


def test_jobs_before_categories_existed_count_as_core(tmp_path):
    conn = db.connect(tmp_path / "x.db")
    for i in range(10):
        db.add_job(conn, f"old {i}", "long")            # no category
    assert topics.pick_category(conn, MIX) != "core"
    assert topics.pick_category(conn, {}) == "core"


def test_discover_asks_for_the_category_and_stores_it(tmp_path):
    conn = db.connect(tmp_path / "x.db")
    seen = {}

    def gen(prompt):
        seen["prompt"] = prompt
        return {"topics": [{"topic": "What if the Moon vanished?", "wikipedia_title": "Tide", "search_query": "what if moon disappeared"}]}

    ids = topics.discover(conn, "science", 1, gen=gen, fetch=lambda t: {"title": "Tide", "url": "u", "text": "x" * 100},
                          min_source_chars=10, score=lambda q: 1.0, category="what_if")
    assert "what if" in seen["prompt"].lower() and conn.execute("SELECT category FROM jobs WHERE id = ?", (ids[0],)).fetchone()[0] == "what_if"


def test_series_suit_the_category():
    assert topics.series_for("what_if") == "what_if" and topics.series_for("core") is None
    assert topics.series_for("history") in ("origin_story", "myth_vs_reality")


_DATA = {"collection": {"items": [
    {"data": [{"nasa_id": "A", "center": "JPL", "title": "Saturn rings", "description": "A view", "media_type": "image"}],
     "links": [{"href": "https://images-assets.nasa.gov/image/A/A~thumb.jpg"}], "href": "https://x/A/collection.json"},
    {"data": [{"nasa_id": "B", "center": "JPL", "title": "Other", "description": "Image used with permission of the artist", "media_type": "image"}],
     "links": [{"href": "u"}], "href": "m"},
    {"data": [{"nasa_id": "C", "center": "", "title": "Unknown source", "description": "", "media_type": "image"}],
     "links": [{"href": "u"}], "href": "m"},
    {"data": [{"nasa_id": "D", "center": "GSFC", "title": "Clip", "description": "", "media_type": "video"}],
     "links": [{"href": "https://images-assets.nasa.gov/video/D/D~thumb.jpg"}], "href": "m"},
]}}


def test_nasa_results_keep_only_nasa_items_without_copyright_notes():
    out = nasa.parse_results(_DATA, "image")
    assert [o["id"] for o in out] == ["A"] and out[0]["artist"] == "NASA/JPL" and out[0]["license"].startswith("NASA")
    assert [o["id"] for o in nasa.parse_results(_DATA, "video")] == ["D"]
    assert "NASA/JPL" in nasa.credit_line(out[0]) and "images.nasa.gov/details/A" in nasa.credit_line(out[0])


def test_gathering_adds_nasa_candidates_only_for_space_topics(monkeypatch, tmp_path):
    from autopilot import shots

    calls = {"nasa": 0}
    monkeypatch.setattr(shots.commons, "search", lambda q: [])
    monkeypatch.setattr(shots.stock, "search", lambda q: [])

    def fake_search(q):
        calls["nasa"] += 1
        return []

    monkeypatch.setattr(shots.nasa, "search_images", fake_search)
    monkeypatch.setattr(shots.nasa, "search_videos", fake_search)
    script = {"title": "T", "sections": [{"heading": "h", "narration": "n"}]}
    gen = lambda p: {"sections": [{"queries": ["a"] * 5, "stock": ["b"] * 3}]}
    shots.gather_images(script, [[(0, 1)]], tmp_path, "topic", gen=gen, use_nasa=False)
    assert calls["nasa"] == 0
    shots.gather_images(script, [[(0, 1)]], tmp_path, "topic", gen=gen, use_nasa=True)
    assert calls["nasa"] > 0
    assert json.dumps({"ok": True})


def test_failed_jobs_do_not_count_and_a_failed_category_can_be_avoided(tmp_path):
    conn = db.connect(tmp_path / "x.db")
    for i in range(6):
        j = db.add_job(conn, f"w{i}", "long", category="what_if")
        conn.execute("UPDATE jobs SET status = 'failed' WHERE id = ?", (j,))
    conn.commit()
    assert topics.pick_category(conn, MIX) == "core"                     # six failures leave the shares where they were
    assert topics.pick_category(conn, MIX, avoid={"core"}) != "core"


def test_daily_chooses_another_topic_when_the_first_fails_for_good(tmp_path, monkeypatch):
    import sys
    import types

    from autopilot import cli
    from autopilot.config import Config

    conn = db.connect(tmp_path / "x.db")
    cfg = Config(niche="s", audience="a", formats={"long": {"per_day": 1, "min_source_chars": 10}}, dry_run=False,
                 topics={"enabled": True, "mix": MIX})
    monkeypatch.setattr(cli.db, "connect", lambda *a, **k: conn)
    monkeypatch.setattr(cli, "load_config", lambda: cfg)
    monkeypatch.setattr(cli, "load_env", lambda: None)
    monkeypatch.setattr(cli, "Stages", lambda *a, **k: types.SimpleNamespace(handlers=dict))
    seen = {"avoid": [], "runs": 0}

    def fake_mix(c, niche, n, mix, avoid=None, **kw):
        seen["avoid"].append(avoid)
        cat = "what_if" if avoid is None else "core"
        return [db.add_job(c, f"topic {len(seen['avoid'])}", "long", category=cat)]

    def fake_run(c, handlers):
        seen["runs"] += 1
        status = "failed" if seen["runs"] == 1 else "done"             # the first topic fails its fact-check three times
        c.execute("UPDATE jobs SET status = ? WHERE status = 'pending'", (status,))
        c.commit()
        return 1

    monkeypatch.setattr(cli.topics, "discover_mix", fake_mix)
    monkeypatch.setattr(cli, "run_pending", fake_run)
    monkeypatch.setattr(sys, "argv", ["autopilot", "daily", "--live"])
    cli.main()                                                          # no SystemExit: a video was finished
    assert seen["runs"] == 2 and seen["avoid"] == [None, {"what_if"}]


def test_nasa_uses_the_preview_picture_not_a_caption_file():
    data = {"collection": {"items": [{
        "data": [{"nasa_id": "V", "center": "JPL", "title": "Clip", "description": "", "media_type": "video"}],
        "links": [{"href": "https://images-assets.nasa.gov/video/V/V.srt", "rel": "captions"},
                  {"href": "https://images-assets.nasa.gov/video/V/V~thumb.jpg", "rel": "preview", "render": "image"}],
        "href": "https://x/V/collection.json"},
        {"data": [{"nasa_id": "W", "center": "JPL", "title": "Only captions", "description": "", "media_type": "video"}],
         "links": [{"href": "https://images-assets.nasa.gov/video/W/W.srt", "rel": "captions"}], "href": "https://x/W/collection.json"}]}}
    out = nasa.parse_results(data, "video")
    assert [o["id"] for o in out] == ["V"] and out[0]["thumb"].endswith("V~thumb.jpg")


def test_a_download_that_is_not_an_image_is_dropped_before_it_is_rated(tmp_path, monkeypatch):
    import pytest

    from autopilot import shots

    bad = tmp_path / "pic.jpg"
    bad.write_text("1\n00:00:02,085 --> 00:00:05,588\nThere aren't many\n")
    monkeypatch.setattr(shots.nasa, "download_thumb", lambda item, cache: bad)
    with pytest.raises(OSError):
        shots._thumb({"source": "nasa", "kind": "image"}, tmp_path)
    assert not bad.exists()
