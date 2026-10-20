import json

import pytest

from autopilot import db, stages, topics
from autopilot.config import Config
from autopilot.pipeline import STAGES, run_pending

CFG = Config(niche="science", audience="en", formats={"long": {"per_day": 1, "target_words": 1500, "min_words": 1150, "min_sections": 6}}, forbidden_topics=["medicine"])
BIG = {"title": "Laser", "text": "x" * 3000}


def _conn(tmp_path):
    return db.connect(tmp_path / "t.db")


def test_discover_dedupes_verifies_and_filters(tmp_path):
    conn = _conn(tmp_path)
    db.add_job(conn, "How lasers work", "long", "Laser")
    out = {"topics": [
        {"topic": "How lasers work", "wikipedia_title": "Laser"},            # duplicate
        {"topic": "Medicine of X rays", "wikipedia_title": "X-ray"},          # forbidden word
        {"topic": "Fake thing", "wikipedia_title": "Nonexistent"},            # no article
        {"topic": "Thin", "wikipedia_title": "Stub"},                         # article too short
        {"topic": "Wrong", "wikipedia_title": "Gravity"},                     # search returned another article
        {"topic": "How transistors work", "wikipedia_title": "Transistor"},   # good
    ]}
    articles = {"Stub": {"title": "Stub", "text": "short"}, "Gravity": {"title": "Banana", "text": "x" * 3000},
                "Transistor": {"title": "Transistor", "text": "x" * 3000}}
    ids = topics.discover(conn, "science", 3, gen=lambda p: out, fetch=articles.get, forbidden=["medicine"])
    assert len(ids) == 1
    assert conn.execute("SELECT source_title FROM jobs WHERE id = ?", (ids[0],)).fetchone()[0] == "Transistor"


def test_qa_rejection_deletes_script_resets_stage_and_saves_feedback(tmp_path, monkeypatch):
    conn = _conn(tmp_path)
    jid = db.add_job(conn, "lasers", "long", "Laser")
    conn.execute("UPDATE jobs SET stage = 'script' WHERE id = ?", (jid,))
    st = stages.Stages(conn, CFG, root=tmp_path / "out", work=tmp_path / "work")
    job = conn.execute("SELECT * FROM jobs").fetchone()
    d = st.dir(job)
    (d / "script.json").write_text("{}")
    (d / "source.json").write_text(json.dumps(BIG))
    monkeypatch.setattr(stages.qa, "check_script", lambda *a, **k: ["unsupported claim: x"])
    with pytest.raises(stages.StageError):
        st.qa(job)
    assert not (d / "script.json").exists()
    assert json.loads((d / "qa_issues.json").read_text()) == ["unsupported claim: x"]
    assert conn.execute("SELECT stage FROM jobs").fetchone()[0] == "new"


def test_script_stage_passes_qa_feedback_and_is_idempotent(tmp_path, monkeypatch):
    conn = _conn(tmp_path)
    db.add_job(conn, "lasers", "long", "Laser")
    st = stages.Stages(conn, CFG, root=tmp_path / "out", work=tmp_path / "work")
    job = conn.execute("SELECT * FROM jobs").fetchone()
    d = st.dir(job)
    (d / "qa_issues.json").write_text(json.dumps(["fix me"]))
    seen = []
    monkeypatch.setattr(stages.wiki, "fetch_source", lambda t: BIG)
    monkeypatch.setattr(stages, "generate_script", lambda *a, feedback=None, **k: seen.append(feedback) or {"title": "t"})
    st.script(job)
    st.script(job)  # second call must not regenerate
    assert seen == [["fix me"]] and (d / "script.json").exists()


def test_qa_failure_loops_back_then_job_fails_after_three_attempts(tmp_path, monkeypatch):
    conn = _conn(tmp_path)
    db.add_job(conn, "lasers", "long", "Laser")
    st = stages.Stages(conn, CFG, root=tmp_path / "out", work=tmp_path / "work")
    monkeypatch.setattr(stages.wiki, "fetch_source", lambda t: BIG)
    monkeypatch.setattr(stages, "generate_script", lambda *a, **k: {"title": "t"})
    monkeypatch.setattr(stages.qa, "check_script", lambda *a, **k: ["bad"])
    for _ in range(3):
        run_pending(conn, st.handlers())
    row = conn.execute("SELECT * FROM jobs").fetchone()
    assert row["status"] == "failed" and row["attempts"] == 3 and "QA rejected" in row["error"]
    assert set(st.handlers()) == set(STAGES)


def _upload_setup(tmp_path, monkeypatch):
    from autopilot import upload as up

    cfg = Config(niche="s", audience="en", formats={"long": {"per_day": 1}}, dry_run=False)
    conn = _conn(tmp_path)
    jid = db.add_job(conn, "lasers", "long", "Laser")
    st = stages.Stages(conn, cfg, root=tmp_path / "out", work=tmp_path / "work")
    d = st.dir(conn.execute("SELECT * FROM jobs").fetchone())
    (d / "script.json").write_text(json.dumps({"title": "T", "description": "d", "tags": []}))
    (d / "timings.json").write_text(json.dumps([{"start": 0, "heading": "a"}]))
    (d / "credits.json").write_text("[]")
    return up, conn, st, jid


def test_upload_saves_video_id_before_thumbnail_and_never_reuploads(tmp_path, monkeypatch):
    up, conn, st, _jid = _upload_setup(tmp_path, monkeypatch)
    inserts = []
    monkeypatch.setattr(up, "insert_video", lambda *a, **k: inserts.append(1) or "VID1")

    def boom(video_id, thumb):
        raise RuntimeError("403 forbidden")

    monkeypatch.setattr(up, "set_thumbnail", boom)
    for _ in range(3):  # simulates the retry loop; thumbnail failure is non-fatal, so run each time
        st.upload(conn.execute("SELECT * FROM jobs").fetchone())
    row = conn.execute("SELECT * FROM jobs").fetchone()
    assert inserts == [1] and row["video_id"] == "VID1" and row["thumbnail_set"] == 0


def test_thumbnail_retry_sets_flag_when_it_finally_works(tmp_path, monkeypatch):
    up, conn, st, jid = _upload_setup(tmp_path, monkeypatch)
    monkeypatch.setattr(up, "insert_video", lambda *a, **k: "VID1")
    monkeypatch.setattr(up, "set_thumbnail", lambda v, t: (_ for _ in ()).throw(RuntimeError("403")))
    st.upload(conn.execute("SELECT * FROM jobs").fetchone())
    monkeypatch.setattr(up, "set_thumbnail", lambda v, t: None)
    assert st.set_thumbnail(jid, "VID1", tmp_path / "t.jpg") is True
    assert conn.execute("SELECT thumbnail_set FROM jobs").fetchone()[0] == 1


def test_db_migration_adds_thumbnail_column_to_old_database(tmp_path):
    import sqlite3

    path = tmp_path / "old.db"
    old = sqlite3.connect(path)
    old.execute("CREATE TABLE jobs (id INTEGER PRIMARY KEY, topic TEXT NOT NULL, kind TEXT NOT NULL, "
                "stage TEXT NOT NULL DEFAULT 'new', status TEXT NOT NULL DEFAULT 'pending', "
                "attempts INTEGER NOT NULL DEFAULT 0, error TEXT, video_id TEXT, source_title TEXT, created_at TEXT)")
    old.commit()
    old.close()
    conn = db.connect(path)
    assert "thumbnail_set" in {r[1] for r in conn.execute("PRAGMA table_info(jobs)")}


def _repair_setup(tmp_path, monkeypatch, check_results):
    cfg = Config(niche="s", audience="en", formats={"long": {"per_day": 1, "target_words": 1500, "min_words": 10, "min_sections": 2}})
    conn = _conn(tmp_path)
    db.add_job(conn, "lasers", "long", "Laser")
    st = stages.Stages(conn, cfg, root=tmp_path / "out", work=tmp_path / "work")
    job = conn.execute("SELECT * FROM jobs").fetchone()
    d = st.dir(job)
    script = {"title": "T", "series": "how_it_works", "sections": [
        {"heading": "A", "narration": "alpha " * 200, "claims": ["lasers emit coherent light"], "key_points": []},
        {"heading": "B", "narration": "beta " * 200, "claims": ["the concept drives research into energy limits"], "key_points": []},
    ]}
    (d / "script.json").write_text(json.dumps(script))
    (d / "source.json").write_text(json.dumps(BIG))
    results = iter(check_results)
    monkeypatch.setattr(stages.qa, "check_script", lambda *a, **k: next(results))
    return conn, st, job, d


def test_qa_repairs_flagged_section_in_place_without_regenerating(tmp_path, monkeypatch):
    conn, st, job, d = _repair_setup(tmp_path, monkeypatch, [
        ["unsupported claim: concept drives research into energy limits"], []])
    seen = {}

    def fake_repair(script, source, targets, bad):
        seen.update(targets=targets, bad=bad)
        script["sections"][1]["narration"] = "fixed " * 200
        return script

    monkeypatch.setattr(stages, "repair_sections", fake_repair)
    st.qa(job)  # no exception: repaired and re-checked clean
    saved = json.loads((d / "script.json").read_text())
    assert seen["targets"] == [1] and saved["sections"][1]["narration"].startswith("fixed")
    assert saved["sections"][0]["narration"].startswith("alpha")  # untouched
    assert conn.execute("SELECT stage FROM jobs").fetchone()[0] == "new"  # stage never advanced or reset


def test_qa_rejects_after_repair_rounds_are_exhausted(tmp_path, monkeypatch):
    bad = ["unsupported claim: concept drives research into energy limits"]
    _conn, st, job, d = _repair_setup(tmp_path, monkeypatch, [bad, bad, bad])
    monkeypatch.setattr(stages, "repair_sections", lambda script, *a: script)
    with pytest.raises(stages.StageError):
        st.qa(job)
    assert not (d / "script.json").exists() and (d / "qa_issues.json").exists()


def test_structural_issues_are_not_repaired_in_place(tmp_path, monkeypatch):
    _conn, st, job, _d = _repair_setup(tmp_path, monkeypatch, [["too short: 10 words < 1150"]])
    called = []
    monkeypatch.setattr(stages, "repair_sections", lambda *a: called.append(1))
    with pytest.raises(stages.StageError):
        st.qa(job)
    assert not called


def test_discover_logs_why_each_candidate_was_rejected(tmp_path, capsys):
    conn = _conn(tmp_path)
    db.add_job(conn, "dup topic", "long", "Dup")
    out = {"topics": [
        {"topic": "dup topic", "wikipedia_title": "Dup"},
        {"topic": "x", "wikipedia_title": "Nope"},
        {"topic": "y", "wikipedia_title": "Stub"},
    ]}
    articles = {"Stub": {"title": "Stub", "text": "short"}}
    assert topics.discover(conn, "science", 1, gen=lambda p: out, fetch=articles.get) == []
    log = capsys.readouterr().out
    assert "proposed 3 candidate" in log and "already covered" in log
    assert "no Wikipedia article found" in log and "too thin" in log


def test_discover_tolerates_renamed_key_and_bare_list(tmp_path):
    conn = _conn(tmp_path)
    good = {"title": "Transistor", "text": "x" * 3000}
    cand = [{"topic": "How transistors work", "wikipedia_title": "Transistor"}]
    ids = topics.discover(conn, "science", 1, gen=lambda p: {"suggestions": cand}, fetch=lambda t: good)
    assert len(ids) == 1
    conn2 = db.connect(tmp_path / "t2.db")
    assert len(topics.discover(conn2, "science", 1, gen=lambda p: cand, fetch=lambda t: good)) == 1
