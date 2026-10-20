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
