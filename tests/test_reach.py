from datetime import datetime, timedelta, timezone

from autopilot import db, demand, schedule, stages, topics
from autopilot.config import Config


# ---------- demand ----------
def _fake_suggest(table):
    return lambda q: table.get(q, [])


def test_question_found_after_fewer_words_scores_higher_than_one_found_late():
    early = _fake_suggest({"why is": ["why is the sky blue", "why is it"]})
    late = _fake_suggest({"why is the sky": ["why is the sky blue", "why is the sky so high"]})
    q = "why is the sky blue"
    assert demand.demand_score(q, early) > demand.demand_score(q, late) > 0


def test_higher_rank_scores_higher_and_unknown_questions_score_zero():
    top = _fake_suggest({"how do": ["how do mri machines work", "how do planes fly"]})
    low = _fake_suggest({"how do": ["how do planes fly", "how do birds fly", "how do mri machines work"]})
    q = "how do mri machines work"
    assert demand.demand_score(q, top) > demand.demand_score(q, low) > 0
    assert demand.demand_score("why does a prince rupert drop explode", _fake_suggest({})) == 0.0
    assert demand.demand_score("single", _fake_suggest({})) == 0.0


def test_a_suggestion_with_a_tail_still_counts_as_the_question():
    s = _fake_suggest({"why is": ["why is the sky blue in tamil"]})
    assert demand.demand_score("why is the sky blue", s) > 0


def test_suggest_fails_soft_when_the_network_is_down(monkeypatch):
    monkeypatch.setattr(demand.urllib.request, "urlopen", lambda *a, **k: (_ for _ in ()).throw(OSError("down")))
    assert demand.suggest("why is") == []


# ---------- topic choice ----------
BIG = {"title": "X", "text": "x" * 3000}


def _conn(tmp_path):
    return db.connect(tmp_path / "t.db")


def test_discover_prefers_the_topic_people_actually_search_for(tmp_path, capsys):
    conn = _conn(tmp_path)
    out = {"topics": [
        {"topic": "Obscure A", "wikipedia_title": "A", "search_query": "what is obscure a"},
        {"topic": "Why the sky is blue", "wikipedia_title": "Rayleigh scattering", "search_query": "why is the sky blue"},
        {"topic": "Obscure B", "wikipedia_title": "B", "search_query": "what is obscure b"},
    ]}
    scores = {"why is the sky blue": 0.9}
    ids = topics.discover(conn, "science", 1, gen=lambda p: out, fetch=lambda t: {"title": t, "text": "x" * 3000},
                          score=lambda q: scores.get(q, 0.0))
    assert conn.execute("SELECT topic FROM jobs WHERE id = ?", (ids[0],)).fetchone()[0] == "Why the sky is blue"
    assert "search demand 0.90" in capsys.readouterr().out


def test_discover_falls_back_to_model_order_and_says_so_when_there_is_no_demand_signal(tmp_path, capsys):
    conn = _conn(tmp_path)
    out = {"topics": [{"topic": "First", "wikipedia_title": "F", "search_query": "q1"},
                      {"topic": "Second", "wikipedia_title": "S", "search_query": "q2"}]}
    ids = topics.discover(conn, "science", 1, gen=lambda p: out, fetch=lambda t: {"title": t, "text": "x" * 3000},
                          score=lambda q: 0.0)
    assert conn.execute("SELECT topic FROM jobs WHERE id = ?", (ids[0],)).fetchone()[0] == "First"
    assert "no search-demand signal" in capsys.readouterr().out


def test_discover_asks_for_extra_candidates_and_a_search_query(tmp_path):
    prompts = []
    topics.discover(_conn(tmp_path), "science", 2, gen=lambda p: prompts.append(p) or {"topics": []},
                    fetch=lambda t: None, score=lambda q: 0.0)
    assert "10 topics" in prompts[0] and "search_query" in prompts[0]  # 2 slots x 5 candidates


# ---------- scheduling ----------
def test_next_slot_today_if_far_enough_otherwise_tomorrow():
    run = datetime(2026, 10, 21, 8, 20, tzinfo=timezone.utc)
    assert schedule.next_slot(15, run) == datetime(2026, 10, 21, 15, 0, tzinfo=timezone.utc)
    late = datetime(2026, 10, 21, 14, 50, tzinfo=timezone.utc)  # only 10 minutes before the slot
    assert schedule.next_slot(15, late) == datetime(2026, 10, 22, 15, 0, tzinfo=timezone.utc)
    after = datetime(2026, 10, 21, 18, 0, tzinfo=timezone.utc)
    assert schedule.next_slot(15, after) == datetime(2026, 10, 22, 15, 0, tzinfo=timezone.utc)


def test_rfc3339_round_trip():
    dt = datetime(2026, 10, 21, 15, 0, tzinfo=timezone.utc)
    assert schedule.rfc3339(dt) == "2026-10-21T15:00:00Z" and schedule.parse("2026-10-21T15:00:00Z") == dt


# ---------- the long video upload schedules itself; Shorts follow it ----------
def _upload_job(tmp_path, privacy, hour=15):
    import json

    cfg = Config(niche="s", audience="en", formats={"long": {"per_day": 1, "publish_hour_utc": hour}}, dry_run=False)
    conn = _conn(tmp_path)
    db.add_job(conn, "lasers", "long", "Laser")
    st = stages.Stages(conn, cfg, root=tmp_path / "out", work=tmp_path / "work", privacy=privacy)
    job = conn.execute("SELECT * FROM jobs").fetchone()
    d = st.dir(job)
    (d / "script.json").write_text(json.dumps({"title": "T", "description": "d", "tags": []}))
    (d / "timings.json").write_text(json.dumps([{"start": 0, "heading": "a"}]))
    (d / "credits.json").write_text("[]")
    return conn, st, job


def test_public_long_video_is_scheduled_for_prime_time_and_the_time_is_saved(tmp_path, monkeypatch):
    from autopilot import upload as up

    conn, st, job = _upload_job(tmp_path, "public")
    seen = {}
    monkeypatch.setattr(up, "insert_video", lambda *a, **k: seen.update(kw=k) or "VID")
    monkeypatch.setattr(up, "set_thumbnail", lambda v, t: None)
    st.upload(job)
    assert seen["kw"]["publish_at"].endswith("T15:00:00Z")
    assert conn.execute("SELECT publish_at FROM jobs").fetchone()[0] == seen["kw"]["publish_at"]


def test_private_long_video_is_not_scheduled(tmp_path, monkeypatch):
    from autopilot import upload as up

    conn, st, job = _upload_job(tmp_path, "private")
    seen = {}
    monkeypatch.setattr(up, "insert_video", lambda *a, **k: seen.update(kw=k) or "VID")
    monkeypatch.setattr(up, "set_thumbnail", lambda v, t: None)
    st.upload(job)
    assert seen["kw"]["publish_at"] is None and conn.execute("SELECT publish_at FROM jobs").fetchone()[0] is None


def test_shorts_are_scheduled_relative_to_the_long_videos_go_live_time(tmp_path, monkeypatch):
    import json

    from autopilot import upload as up

    conn, st, job = _upload_job(tmp_path, "public")
    conn.execute("UPDATE jobs SET video_id = 'PARENT', publish_at = '2026-10-21T15:00:00Z' WHERE id = ?", (job["id"],))
    conn.commit()
    kid_id = db.add_job(conn, "kid", "short", parent_id=job["id"], short_idx=0)
    kid = conn.execute("SELECT * FROM jobs WHERE id = ?", (kid_id,)).fetchone()
    kd = st.dir(kid)
    (kd / "script.json").write_text(json.dumps({"title": "T", "narration": "Hook sentence. More."}))
    (kd / "final.mp4").write_bytes(b"x")
    seen = {}
    monkeypatch.setattr(up, "insert_video", lambda *a, **k: seen.update(kw=k) or "SHORT")
    st.short_upload(kid)
    assert seen["kw"]["publish_at"] == "2026-10-21T17:00:00Z"  # 15:00 + the first offset (2 h)
    assert timedelta(0) < schedule.parse(seen["kw"]["publish_at"]) - schedule.parse("2026-10-21T15:00:00Z") <= timedelta(hours=2)


def test_long_queries_are_scored_by_their_opening_words_at_a_discount():
    table = {"what is quantum": ["what is quantum entanglement", "what is quantum computing"]}
    s = _fake_suggest(table)
    long_q = "what is quantum entanglement and how does it work"
    short_q = "what is quantum entanglement"
    assert demand.demand_score(long_q, s) > 0                       # found via its first 4 words
    assert demand.demand_score(long_q, s) < demand.demand_score(short_q, s)  # but worth less than the short form


def test_topic_prompt_asks_for_short_as_typed_queries(tmp_path):
    prompts = []
    topics.discover(_conn(tmp_path), "science", 1, gen=lambda p: prompts.append(p) or {"topics": []},
                    fetch=lambda t: None, score=lambda q: 0.0)
    assert "SHORT, 3-6 words" in prompts[0]
