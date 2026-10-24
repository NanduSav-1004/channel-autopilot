import numpy as np

from autopilot import malayalam as ml


def test_malayalam_sentences_split_without_capitals():
    assert ml.split_sentences_ml("ഇത് ഒന്ന്. ഇത് രണ്ട്? ഇത് മൂന്ന്!") == ["ഇത് ഒന്ന്.", "ഇത് രണ്ട്?", "ഇത് മൂന്ന്!"]


def _tone(seconds, rate=24000, amp=8000):
    t = np.arange(int(seconds * rate)) / rate
    return (np.sin(2 * np.pi * 220 * t) * amp).astype("<i2")


def test_alignment_finds_the_pauses_and_trims_silence_and_tail_noise():
    rate = 24000
    quiet = np.zeros(int(0.5 * rate), dtype="<i2")
    pcm = np.concatenate([quiet, _tone(2.0), np.zeros(int(0.4 * rate), dtype="<i2"), _tone(2.0), quiet, quiet]).tobytes()
    sentences = ["അ" * 20, "അ" * 20]
    out, spans = ml.align_by_silence(sentences, pcm, rate)
    assert len(out) / 2 / rate < 5.2                       # leading and trailing silence cut
    (a0, b0), (a1, b1) = spans
    assert a0 == 0 and abs(b0 - 2.4) < 0.5 and abs(a1 - b0) < 1e-6 and b1 > a1 + 1.5   # boundary sits in the real pause


def test_ml_quota_swaps_and_restores_environment(monkeypatch):
    import os

    monkeypatch.setenv("GEMINI_API_KEY", "english")
    monkeypatch.setenv("GROQ_API_KEY", "groq")
    monkeypatch.setenv("GEMINI_API_KEY_ML", "malayalam")
    with ml.ml_quota():
        assert os.environ["GEMINI_API_KEY"] == "malayalam" and "GROQ_API_KEY" not in os.environ
    assert os.environ["GEMINI_API_KEY"] == "english" and os.environ["GROQ_API_KEY"] == "groq"


def test_translate_script_keeps_sections_and_shortens_long_titles():
    script = {"title": "T", "thumbnail_text": "X", "description": "D", "series": "how_it_works",
              "sections": [{"heading": "H1", "narration": "One."}, {"heading": "H2", "narration": "Two."}]}
    calls = []

    def gen(prompt):
        calls.append(prompt)
        if "metadata" in prompt:
            return {"title": "ത" * 90, "thumbnail_text": "ചൂട് വെള്ളം", "description": "വിവരണം", "tags": ["a"]}
        if "Shorten" in prompt:
            return {"title": "ചെറിയ തലക്കെട്ട് ഇവിടെ"}
        return {"heading": "ശീർഷകം", "narration": "വിവർത്തനം."}

    out = ml.translate_script(script, gen=gen)
    assert [s["narration"] for s in out["sections"]] == ["വിവർത്തനം."] * 2 and len(out["title"]) <= 70


def test_missing_numbers_are_found_exactly():
    assert ml.missing_numbers("In 1963 about 1,500 students and 3 teachers.", "1963-ൽ 1,500 വിദ്യാർത്ഥികൾ.") == ["3"]
    assert ml.missing_numbers("No numbers here.", "ഒന്നുമില്ല") == []


def test_a_bad_translation_is_repaired_with_the_problems_as_feedback():
    sec = {"heading": "H", "narration": "Mpemba was 13 years old in 1963."}
    prompts = []

    def gen(prompt):
        prompts.append(prompt)
        if prompt.startswith("You check"):
            return {"issues": []}
        if "reviewer found" in prompt:
            return {"heading": "ശീ", "narration": "1963-ൽ എംപെംബയ്ക്ക് 13 വയസ്സ്."}
        return {"heading": "ശീ", "narration": "എംപെംബയ്ക്ക് 13 വയസ്സ്."}        # the year was dropped

    out = ml.translate_section(sec, gen, log=lambda s: None)
    assert "1963" in out["narration"] and any("reviewer found" in p and "1963" in p for p in prompts)


def test_a_translation_that_stays_wrong_rejects_the_edition():
    import pytest

    def gen(prompt):
        if prompt.startswith("You check"):
            return {"issues": ["the Malayalam says the opposite"]}
        if prompt.startswith("A reviewer compared"):
            return {"real": [True]}
        return {"heading": "ശീ", "narration": "തെറ്റ്."}

    with pytest.raises(ml.TranslationRejected):
        ml.translate_section({"heading": "H", "narration": "True."}, gen, log=lambda s: None)


def test_edition_due_picks_todays_uploaded_video_without_a_malayalam_edition(tmp_path):
    from autopilot import db

    conn = db.connect(tmp_path / "x.db")
    a = db.add_job(conn, "old", "long")
    b = db.add_job(conn, "new", "long")
    conn.execute("UPDATE jobs SET video_id = 'V1', created_at = datetime('now', '-3 days') WHERE id = ?", (a,))
    conn.execute("UPDATE jobs SET video_id = 'V2' WHERE id = ?", (b,))
    conn.commit()
    assert ml.edition_due(conn)["id"] == b
    conn.execute("UPDATE jobs SET ml_status = 'failed: X' WHERE id = ?", (b,))
    assert ml.edition_due(conn) is None
    conn.execute("UPDATE jobs SET ml_status = NULL, ml_video_id = 'M' WHERE id = ?", (b,))
    assert ml.edition_due(conn) is None


def test_daily_edition_skips_cleanly_without_a_malayalam_login(tmp_path, monkeypatch):
    from autopilot import db
    from autopilot.config import Config

    monkeypatch.setenv("GEMINI_API_KEY_ML", "k")
    monkeypatch.delenv("YOUTUBE_REFRESH_TOKEN_ML", raising=False)
    monkeypatch.setattr("autopilot.youtube_auth.TOKEN_PATH_ML", tmp_path / "none.json")
    cfg = Config(niche="s", audience="a", formats={}, malayalam={"enabled": True})
    msg = ml.run_daily_edition(db.connect(tmp_path / "x.db"), cfg, "public", True, tmp_path)
    assert "no Malayalam channel login" in msg
    assert "disabled" in ml.run_daily_edition(db.connect(tmp_path / "y.db"), Config("s", "a", {}), "public", True, tmp_path)


def test_the_reviewers_false_alarm_is_dropped_by_the_second_look():
    def gen(prompt):
        if prompt.startswith("You check"):
            return {"issues": ["a confused complaint"]}
        if prompt.startswith("A reviewer compared"):
            return {"real": [False]}
        raise AssertionError(prompt)

    assert ml.check_translation("English.", "മലയാളം.", gen) == []
