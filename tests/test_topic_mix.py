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
     "links": [{"href": "u"}], "href": "m"},
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
