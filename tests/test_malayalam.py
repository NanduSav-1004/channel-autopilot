import itertools
import wave

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


def test_daily_edition_does_nothing_without_a_due_video_or_when_disabled(tmp_path, monkeypatch):
    from autopilot import db
    from autopilot.config import Config

    monkeypatch.setenv("GEMINI_API_KEY_ML", "k")
    monkeypatch.delenv("YOUTUBE_REFRESH_TOKEN_ML", raising=False)
    monkeypatch.setattr("autopilot.youtube_auth.TOKEN_PATH_ML", tmp_path / "none.json")
    cfg = Config(niche="s", audience="a", formats={}, malayalam={"enabled": True})
    msg = ml.run_daily_edition(db.connect(tmp_path / "x.db"), cfg, "public", True, tmp_path)
    assert "nothing due" in msg
    assert "disabled" in ml.run_daily_edition(db.connect(tmp_path / "y.db"), Config("s", "a", {}), "public", True, tmp_path)


def test_the_reviewers_false_alarm_is_dropped_by_the_second_look():
    def gen(prompt):
        if prompt.startswith("You check"):
            return {"issues": ["a confused complaint"]}
        if prompt.startswith("A reviewer compared"):
            return {"real": [False]}
        raise AssertionError(prompt)

    assert ml.check_translation("English.", "മലയാളം.", gen) == []


def test_segment_by_pauses_cuts_at_the_real_pauses_even_when_the_pace_varies():
    # sentences of 40, 20 and 40 letters spoken at slightly different paces, with a comma pause inside the middle one
    gaps = [(3.0, 3.15), (6.4, 6.9), (8.5, 8.6), (10.9, 11.4), (14.0, 14.1)]      # (3.0..) (8.5..) (14.0..) are only commas
    spans = ml.segment_by_pauses([40, 20, 40], gaps, 0.0, 17.4)
    assert abs(spans[0][1] - 6.4) < 0.2 and abs(spans[1][0] - 6.9) < 0.2
    assert abs(spans[1][1] - 10.9) < 0.2 and abs(spans[2][0] - 11.4) < 0.2 and spans[2][1] == 17.4


def test_segment_by_pauses_falls_back_to_proportional_cuts_without_pauses():
    spans = ml.segment_by_pauses([10, 10, 20], [], 0.0, 40.0)
    assert [round(a) for a, _ in spans] == [0, 10, 20] and spans[-1][1] == 40.0


def test_word_times_fill_the_span_in_order():
    words = ml.words_in((2.0, 4.0), ["അ" * 3, "അ" * 1, "അ" * 4])
    assert words[0]["s"] == 2.0 and words[-1]["e"] == 4.0 and all(a["e"] <= b["s"] + 1e-6 for a, b in itertools.pairwise(words))


def test_timing_from_audio_with_pauses(tmp_path):
    rate = 24000
    tone = lambda sec: (np.sin(2 * np.pi * 220 * np.arange(int(sec * rate)) / rate) * 8000).astype("<i2")
    gap = lambda sec: np.zeros(int(sec * rate), dtype="<i2")
    audio = np.concatenate([gap(0.3), tone(3.0), gap(0.5), tone(1.5), gap(0.5), tone(3.0), gap(0.6)])
    wav = tmp_path / "n.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(audio.tobytes())
    sents = [{"text": "അ" * 30 + ".", "start": 0, "end": 3.8}, {"text": "അ" * 15 + ".", "start": 3.8, "end": 5.8},
             {"text": "അ" * 30 + ".", "start": 5.8, "end": 9.4}]
    timings = [{"heading": "h", "start": 0.0, "end": audio.size / rate, "sentences": sents}]
    assert ml.ml_add_word_times(wav, timings) == 1
    ml.make_monotone(timings)
    s = timings[0]["sentences"]
    assert abs(s[1]["start"] - 3.8) < 0.3 and abs(s[2]["start"] - 5.8) < 0.3 and s[0]["words"] and ml.pace_outliers(timings) == 0
