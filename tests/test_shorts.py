import itertools
import json
import shutil
import subprocess
import wave
from datetime import datetime, timezone

import pytest
from PIL import Image

from autopilot import db, render, shorts, stages
from autopilot.config import Config
from autopilot.errors import TransientError
from autopilot.pipeline import SHORT_STAGES, STAGES, run_pending

SOURCE = {"title": "Laser", "url": "https://en.wikipedia.org/wiki/Laser", "text": "x" * 3000}
SCRIPT = {"title": "How lasers work", "sections": [
    {"heading": f"H{i}", "narration": f"section {i} text"} for i in range(5)]}


def _narr(words=100):
    return ("Did you know lasers are special. " + "word " * (words - 6)).strip() + "."


def _plan_out(*idx_words):
    return {"shorts": [{"section_index": i, "title": f"T{i}", "narration": _narr(w)} for i, w in idx_words]}


def test_plan_shorts_drops_bad_lengths_duplicates_and_out_of_range():
    out = _plan_out((0, 100), (1, 20), (2, 400), (0, 100), (9, 100), (3, 100))
    out["shorts"].append({"section_index": 4, "title": "", "narration": _narr()})  # no title
    calls = []

    def gen(prompt):
        calls.append(prompt)
        return out if len(calls) == 1 else {"unsupported": [], "advice_given": False}

    res = shorts.plan_shorts(SCRIPT, SOURCE, 3, gen=gen)
    assert [s["section_index"] for s in res] == [0, 3]
    assert "Write 6 standalone" in calls[0] and "HARD limit" in calls[0]  # asks for twice as many, with a hard word limit


def test_plan_shorts_drops_only_the_short_the_factchecker_flagged():
    seen = {}

    def gen(prompt):
        if "Write" in prompt and "standalone" in prompt:
            return _plan_out((0, 100), (1, 100), (2, 100))
        seen["claims"] = prompt
        return {"unsupported": ["[short 1] Did you know lasers are special."], "advice_given": False}

    res = shorts.plan_shorts(SCRIPT, SOURCE, 3, gen=gen)
    assert [s["section_index"] for s in res] == [0, 2] and "[short 2]" in seen["claims"]


def test_plan_shorts_unattributable_failure_or_advice_drops_everything():
    plan = _plan_out((0, 100), (1, 100))
    assert shorts.plan_shorts(SCRIPT, SOURCE, 2, gen=lambda p: plan if "standalone" in p else
                              {"unsupported": ["something vague"], "advice_given": False}) == []
    assert shorts.plan_shorts(SCRIPT, SOURCE, 2, gen=lambda p: plan if "standalone" in p else
                              {"unsupported": [], "advice_given": True}) == []


def test_caption_chunks_cover_the_sentence_timing_without_orphans():
    sent = [{"text": "one two three four five six seven eight", "start": 2.0, "end": 6.0}]
    chunks = shorts.caption_chunks(sent, max_words=6)
    assert len(chunks) == 1 and chunks[0][1] == 2.0 and chunks[0][2] == pytest.approx(6.0)  # 6+2 words merged
    sent = [{"text": " ".join(f"w{i}" for i in range(14)), "start": 0.0, "end": 7.0}]
    chunks = shorts.caption_chunks(sent, max_words=6)
    assert all(a[2] == pytest.approx(b[1]) for a, b in itertools.pairwise(chunks))
    assert chunks[-1][2] == pytest.approx(7.0) and all(len(c[0].split()) >= 3 for c in chunks)


def test_publish_times_spread_through_the_day_and_wrap():
    now = datetime(2026, 10, 21, 8, 0, 0, tzinfo=timezone.utc)
    assert shorts.publish_times(3, [2, 6, 10], now) == ["2026-10-21T10:00:00Z", "2026-10-21T14:00:00Z", "2026-10-21T18:00:00Z"]
    assert shorts.publish_times(4, [2, 6, 10], now)[3] == "2026-10-21T22:00:00Z"  # wraps +12h


def test_short_description_links_to_the_full_video_and_trims_credits():
    d = shorts.short_description("A hook.", "VID123", "https://src", ["c" * 100] * 200)
    assert "https://youtu.be/VID123" in d and "AI-assisted" in d and len(d) <= 5000 and "more (see the full video)" in d


# ---------- stage handlers ----------
CFG = Config(niche="s", audience="en", formats={"long": {"per_day": 1}, "short": {"per_day": 2}}, dry_run=False)


def _setup(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    pid = db.add_job(conn, "lasers", "long", "Laser")
    st = stages.Stages(conn, CFG, root=tmp_path / "out", work=tmp_path / "work", privacy="public")
    parent = conn.execute("SELECT * FROM jobs WHERE id = ?", (pid,)).fetchone()
    d = st.dir(parent)
    (d / "script.json").write_text(json.dumps(SCRIPT))
    (d / "source.json").write_text(json.dumps(SOURCE))
    return conn, st, pid, d


def test_shorts_stage_queues_child_jobs_once_and_places_them_inside_the_parent_folder(tmp_path, monkeypatch):
    conn, st, pid, d = _setup(tmp_path)
    plans = [{"section_index": 1, "title": "A", "narration": "n"}, {"section_index": 3, "title": "B", "narration": "n"}]
    monkeypatch.setattr(shorts, "plan_shorts", lambda *a, **k: plans)
    parent = conn.execute("SELECT * FROM jobs WHERE id = ?", (pid,)).fetchone()
    st.shorts(parent)
    st.shorts(parent)  # idempotent
    kids = conn.execute("SELECT * FROM jobs WHERE parent_id = ? ORDER BY short_idx", (pid,)).fetchall()
    assert [(k["kind"], k["short_idx"], k["topic"]) for k in kids] == [("short", 0, "A"), ("short", 1, "B")]
    assert st.dir(kids[1]) == d / "short1"


def test_shorts_stage_skips_quietly_when_the_long_videos_files_are_gone(tmp_path, monkeypatch):
    conn, st, pid, d = _setup(tmp_path)
    (d / "source.json").unlink()
    monkeypatch.setattr(shorts, "plan_shorts", lambda *a, **k: pytest.fail("must not regenerate"))
    st.shorts(conn.execute("SELECT * FROM jobs WHERE id = ?", (pid,)).fetchone())
    assert conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 1


def test_run_pending_picks_up_shorts_queued_during_the_run(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    pid = db.add_job(conn, "lasers", "long", "Laser")
    ran = []

    def plan(job):
        ran.append("shorts")
        db.add_job(conn, "kid", "short", parent_id=pid, short_idx=0)

    handlers = {s: (lambda job, s=s: ran.append(s)) for s in STAGES + SHORT_STAGES}
    handlers["shorts"] = plan
    assert run_pending(conn, handlers) == 2
    assert ran[-4:] == SHORT_STAGES
    assert {r["status"] for r in conn.execute("SELECT status FROM jobs")} == {"done"}


def _short_job(conn, pid, idx=0):
    jid = db.add_job(conn, f"S{idx}", "short", parent_id=pid, short_idx=idx)
    return conn.execute("SELECT * FROM jobs WHERE id = ?", (jid,)).fetchone()


def test_short_upload_schedules_when_public_and_links_the_parent(tmp_path, monkeypatch):
    from autopilot import upload as up

    conn, st, pid, _d = _setup(tmp_path)
    conn.execute("UPDATE jobs SET video_id = 'PARENT' WHERE id = ?", (pid,))
    conn.commit()
    job0, job1 = _short_job(conn, pid, 0), _short_job(conn, pid, 1)
    sd = st.dir(job1)
    (sd / "script.json").write_text(json.dumps({"title": "Hot water", "narration": "Hook sentence here. More."}))
    (sd / "final.mp4").write_bytes(b"x")
    seen = {}
    monkeypatch.setattr(up, "insert_video", lambda *a, **k: seen.update(args=a, kw=k) or "SHORTID")
    st.short_upload(job1)
    assert seen["args"][1].endswith("#Shorts") and "youtu.be/PARENT" in seen["args"][2]
    assert seen["kw"]["publish_at"] and conn.execute("SELECT video_id FROM jobs WHERE id = ?", (job1["id"],)).fetchone()[0] == "SHORTID"
    assert job0["id"] != job1["id"]


def test_short_upload_not_scheduled_when_private_and_waits_for_the_parent(tmp_path, monkeypatch):
    from autopilot import upload as up

    conn, st, pid, _d = _setup(tmp_path)
    st.privacy = "private"
    job = _short_job(conn, pid)
    sd = st.dir(job)
    (sd / "script.json").write_text(json.dumps({"title": "T", "narration": "Hook. More."}))
    (sd / "final.mp4").write_bytes(b"x")
    with pytest.raises(TransientError):  # parent has no video_id yet
        st.short_upload(job)
    conn.execute("UPDATE jobs SET video_id = 'P' WHERE id = ?", (pid,))
    conn.commit()
    seen = {}
    monkeypatch.setattr(up, "insert_video", lambda *a, **k: seen.update(kw=k) or "V")
    st.short_upload(job)
    assert seen["kw"]["publish_at"] is None and seen["kw"]["privacy"] == "private"


# ---------- vertical rendering ----------
def test_write_ass_vertical_has_one_event_per_chunk(tmp_path):
    p = tmp_path / "v.ass"
    render.write_ass_vertical([("hello {x}", 0, 1), ("there", 1, 2)], p)
    body = p.read_text()
    assert "PlayResY: 1920" in body and body.count("Dialogue:") == 2 and "{x}" not in body


def test_prep_vertical_outputs_the_oversampled_vertical_canvas(tmp_path):
    src = tmp_path / "a.jpg"
    Image.new("RGB", (1600, 900), (200, 60, 60)).save(src)
    render._prep_vertical(src, tmp_path / "o.jpg")
    assert Image.open(tmp_path / "o.jpg").size == (1620, 2880)


@pytest.mark.skipif(not (shutil.which("ffmpeg") and shutil.which("ffprobe")), reason="needs ffmpeg and ffprobe installed")
def test_render_short_end_to_end_makes_a_1080x1920_video(tmp_path):
    nar = tmp_path / "n.wav"
    with wave.open(str(nar), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(22050)
        w.writeframes(b"\x00\x00" * 22050 * 4)
    timings = [{"heading": "h", "start": 0, "end": 4.0,
                "sentences": [{"text": "Did you know this is a test caption.", "start": 0.2, "end": 3.5}]}]
    img = tmp_path / "i.jpg"
    Image.new("RGB", (1280, 720), (30, 90, 160)).save(img)
    out = tmp_path / "short.mp4"
    render.render_short({"title": "T"}, timings, [{"kind": "image", "path": img}], nar, out, tmp_path / "w")
    info = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                           "stream=width,height:format=duration", "-of", "default=nw=1", str(out)],
                          capture_output=True, text=True, check=True).stdout
    assert "width=1080" in info and "height=1920" in info
    assert 3.5 < float(info.split("duration=")[1]) < 4.6


def test_overlong_drafts_get_one_request_to_shorten_then_pass():
    calls = []

    def gen(prompt):
        calls.append(prompt)
        if "standalone" in prompt:
            return _plan_out((0, 100), (1, 160), (2, 170))  # two are over the limit
        if "AT MOST" in prompt:
            return _plan_out((1, 100), (2, 105))
        return {"unsupported": [], "advice_given": False}

    res = shorts.plan_shorts(SCRIPT, SOURCE, 3, gen=gen)
    assert sorted(s["section_index"] for s in res) == [0, 1, 2]
    assert sum("AT MOST" in c for c in calls) == 1  # asked once, not in a loop


def test_no_shorten_request_when_enough_usable_shorts_already():
    calls = []

    def gen(prompt):
        calls.append(prompt)
        if "standalone" in prompt:
            return _plan_out((0, 100), (1, 100), (2, 100), (3, 200))
        return {"unsupported": [], "advice_given": False}

    shorts.plan_shorts(SCRIPT, SOURCE, 3, gen=gen)
    assert not any("AT MOST" in c for c in calls)


def test_empty_plan_is_not_saved_so_a_later_run_can_retry(tmp_path, monkeypatch):
    conn, st, pid, d = _setup(tmp_path)
    monkeypatch.setattr(shorts, "plan_shorts", lambda *a, **k: [])
    st.shorts(conn.execute("SELECT * FROM jobs WHERE id = ?", (pid,)).fetchone())
    assert not (d / "shorts.json").exists() and conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 1


def test_trim_keeps_hook_and_payoff_and_fits_the_limit():
    sents = ["Hook sentence goes here now."] + [f"Middle fact number {i} has some words in it." for i in range(20)] + ["The payoff lands here."]
    out = shorts.trim_to_limit(" ".join(sents), max_words=40)
    assert out.startswith("Hook sentence") and out.endswith("The payoff lands here.")
    assert len(out.split()) <= 40 and "Middle fact number 0" in out  # kept in order from the front


def test_trim_gives_up_when_hook_and_payoff_alone_are_too_long_and_passes_short_text_through():
    assert shorts.trim_to_limit("a " * 80 + ". " + "b " * 80 + ".", max_words=100) is None
    assert shorts.trim_to_limit("Short one. Short two.", max_words=100) == "Short one. Short two."


def test_plan_shorts_trims_in_code_when_the_model_will_not_comply():
    def long_draft(i):
        sents = ["Hook sentence goes here for this one."] + [f"Fact {i}-{j} is stated clearly in the section text." for j in range(24)] + ["The payoff is clear."]
        return {"section_index": i, "title": f"T{i}", "narration": " ".join(sents)}

    calls = []

    def gen(prompt):
        calls.append(prompt)
        if "standalone" in prompt or "AT MOST" in prompt:
            return {"shorts": [long_draft(0), long_draft(1), long_draft(2)]}  # never complies
        return {"unsupported": [], "advice_given": False}

    res = shorts.plan_shorts(SCRIPT, SOURCE, 3, gen=gen)
    assert len(res) == 3 and all(shorts.MIN_WORDS <= len(s["narration"].split()) <= shorts.MAX_WORDS for s in res)
    assert all(s["narration"].startswith("Hook sentence") and s["narration"].endswith("The payoff is clear.") for s in res)
    assert sum("AT MOST" in c for c in calls) == 1  # one polite request, then code takes over


def test_planner_prompt_includes_each_sections_verified_claims_and_forbids_embellishment():
    script = {"title": "T", "sections": [
        {"heading": "A", "narration": "alpha text", "claims": ["claim one", "claim two"]},
        {"heading": "B", "narration": "beta text"}]}
    prompts = []
    shorts.plan_shorts(script, SOURCE, 1, gen=lambda p: prompts.append(p) or {"shorts": []})
    assert "Verified facts: claim one | claim two" in prompts[0]
    assert prompts[0].count("Verified facts") == 1 and "superlatives" in prompts[0]


def test_unsupported_claims_are_attributed_by_overlap_when_the_tag_is_lost():
    cands = [{"narration": "Lasers emit coherent light of a single wavelength today."},
             {"narration": "A transistor switches current using a small control voltage."}]
    bad, unknown = shorts.attribute_unsupported(
        ["A transistor switches current using a control voltage", "[short 0] anything at all"], cands)
    assert bad == {0, 1} and unknown == []
    bad, unknown = shorts.attribute_unsupported(["bananas grow in warm tropical climates"], cands)
    assert bad == set() and unknown == ["bananas grow in warm tropical climates"]


def test_plan_shorts_drops_only_the_attributed_short_when_tags_are_missing():
    def gen(prompt):
        if "standalone" in prompt:
            return _plan_out((0, 100), (1, 100))
        return {"unsupported": [_narr(100).split(".")[0] + " word word word"], "advice_given": False}

    # both drafts share the same opening sentence, so the first best match (index 0) is the one dropped
    res = shorts.plan_shorts(SCRIPT, SOURCE, 2, gen=gen)
    assert len(res) == 1
