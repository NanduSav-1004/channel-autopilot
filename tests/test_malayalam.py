import itertools
import json
import sqlite3
import subprocess
import sys
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


def test_a_short_may_leave_things_out_but_not_invent_numbers():
    assert ml.added_numbers("Seven years later.", "1950-ൽ ഏഴ് വർഷം.") == ["1950"]
    assert ml.added_numbers("In 1950 it began.", "1950-ൽ തുടങ്ങി.") == []


def test_translate_short_asks_again_when_too_long_and_rejects_invented_numbers():
    import pytest

    short = {"title": "T", "narration": "In 1950 they found it."}
    seen = []

    def gen(prompt):
        seen.append(prompt)
        if prompt.startswith("You check"):
            return {"issues": []}
        if "reviewer found" in prompt:
            return {"title": "ശീർഷകം", "narration": "1950-ൽ അവർ കണ്ടെത്തി."}
        return {"title": "ശീർഷകം", "narration": "അ " * 120}                      # far too long the first time

    out = ml.translate_short(short, 80, gen, log=lambda s: None)
    assert out["narration"] == "1950-ൽ അവർ കണ്ടെത്തി." and any("too long" in p for p in seen)

    with pytest.raises(ml.TranslationRejected):
        ml.translate_short(short, 80, lambda p: {"issues": []} if p.startswith("You check") else
                           {"title": "ശീ", "narration": "2020-ൽ കണ്ടെത്തി."}, log=lambda s: None)


def test_short_description_links_the_malayalam_long_video_and_discloses_ai():
    d = ml.short_description_ml({"narration": "ആദ്യ വാക്യം. രണ്ടാമത്തേത്."}, "LONGID", "https://src", ["credit 1"])
    assert "https://youtu.be/LONGID" in d and "AI" in d and "https://src" in d and "credit 1" in d
    assert "This video uses" not in d


def test_build_short_retries_shorter_and_renders_a_vertical_video(tmp_path):
    import shutil

    import pytest
    from PIL import Image

    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        pytest.skip("needs ffmpeg")
    sdir = tmp_path / "short0"
    sdir.mkdir()
    (sdir / "script.json").write_text(json.dumps({"title": "T", "narration": "One two.", "section_index": 0}))
    img = tmp_path / "i.jpg"
    Image.new("RGB", (1280, 720), (200, 40, 40)).save(img)
    spoken = []

    def speak(ml_script, wav):
        n = len(spoken)
        spoken.append(n)
        secs = 70.0 if n == 0 else 6.0                               # first version is too long for a Short
        with wave.open(str(wav), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000)
            w.writeframes(np.zeros(int(24000 * secs), dtype="<i2").tobytes())
        words = [{"w": "ഒന്ന്", "s": 0.5, "e": 1.0}, {"w": "രണ്ട്.", "s": 1.1, "e": 1.6}]
        return [{"heading": "T", "start": 0.0, "end": secs, "sentences": [{"text": "ഒന്ന് രണ്ട്.", "start": 0.5, "end": 1.6, "words": words}]}]

    asked = []

    def translate(short, max_words):
        asked.append(max_words)
        return {"title": "ശീർഷകം", "narration": "ഒന്ന് രണ്ട്."}

    out = ml.build_short(sdir, [[{"kind": "image", "path": str(img)}]], sdir / "ml", tmp_path / "w", {"name": "Charon"},
                         translate=translate, speak=speak)
    assert len(asked) == 2 and asked[1] < asked[0] and out.exists()
    info = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(out)],
                          capture_output=True, text=True, check=True).stdout
    assert "1080,1920" in info


def test_a_dramatic_pause_inside_a_sentence_is_matched_to_the_right_word_boundary():
    # five words (letters 23, 16, 17, 3, 9) spoken over 0.08-7.02 s with real pauses after word 2 and word 3
    words = ["അ" * 23, "അ" * 16, "അ" * 17, "അ" * 3, "അ" * 9]
    out = ml.place_words(words, [(3.5, 3.78), (4.72, 5.54)], 0.08, 7.02)
    assert abs(out[1]["e"] - 3.5) < 0.05 and abs(out[2]["s"] - 3.78) < 0.05
    assert abs(out[2]["e"] - 4.72) < 0.05 and abs(out[3]["s"] - 5.54) < 0.05
    assert out[0]["s"] == 0.08 and out[-1]["e"] == 7.02


def test_place_words_without_inner_pauses_is_proportional():
    out = ml.place_words(["അ" * 10, "അ" * 10], [], 0.0, 4.0)
    assert abs(out[0]["e"] - 2.0) < 1e-6


def test_a_failed_edition_is_retried_only_when_asked(tmp_path):
    from autopilot import db

    conn = db.connect(tmp_path / "x.db")
    a = db.add_job(conn, "t", "long")
    conn.execute("UPDATE jobs SET video_id = 'V', ml_status = 'failed: OSError' WHERE id = ?", (a,))
    conn.commit()
    assert ml.edition_due(conn) is None and ml.edition_due(conn, retry=True)["id"] == a
    conn.execute("UPDATE jobs SET ml_status = 'built' WHERE id = ?", (a,))
    assert ml.edition_due(conn, retry=True) is None            # a review build is not redone


def test_missing_malayalam_shorts_are_found_when_the_long_video_is_up(tmp_path):
    from autopilot import db

    conn = db.connect(tmp_path / "x.db")
    a = db.add_job(conn, "t", "long")
    s = db.add_job(conn, "s", "short", parent_id=a, short_idx=0)
    conn.execute("UPDATE jobs SET video_id = 'V', ml_video_id = 'M' WHERE id = ?", (a,))
    conn.execute("UPDATE jobs SET video_id = 'S' WHERE id = ?", (s,))
    conn.commit()
    assert ml.shorts_pending(conn)["id"] == a
    conn.execute("UPDATE jobs SET ml_status = 'failed: X' WHERE id = ?", (s,))
    assert ml.shorts_pending(conn) is None and ml.shorts_pending(conn, retry=True)["id"] == a
    conn.execute("UPDATE jobs SET ml_video_id = 'MS', ml_status = 'done' WHERE id = ?", (s,))
    assert ml.shorts_pending(conn, retry=True) is None


def test_media_is_rebuilt_from_the_saved_script_when_the_run_is_gone(tmp_path):
    (tmp_path / "script.json").write_text(json.dumps({"title": "T", "sections": [{"heading": "A", "narration": "word " * 100},
                                                                                {"heading": "B", "narration": "word " * 100}]}))
    timings = ml.estimate_timings(json.loads((tmp_path / "script.json").read_text()))
    assert len(timings) == 2 and timings[1]["start"] == timings[0]["end"]
    seen = {}

    def gather(script, plan, topic):
        seen["plan"], seen["topic"] = plan, topic
        return [[{"kind": "image", "path": tmp_path / "a.jpg"}], []], ["credit"]

    ml.recover_media(tmp_path, timings, "Topic", gather=gather)
    assert seen["topic"] == "Topic" and len(seen["plan"]) == 2
    assert json.loads((tmp_path / "items.json").read_text())[0][0]["kind"] == "image"
    assert json.loads((tmp_path / "credits.json").read_text()) == ["credit"]


def test_the_watchdog_notices_a_missing_malayalam_video(tmp_path):
    sys.path.insert(0, "scripts")
    import watchdog

    c = sqlite3.connect(tmp_path / "a.db")
    c.execute("CREATE TABLE jobs (id INTEGER PRIMARY KEY, kind TEXT, video_id TEXT, created_at TEXT, ml_video_id TEXT, ml_status TEXT)")
    c.execute("INSERT INTO jobs (kind, video_id, created_at, ml_video_id, ml_status) VALUES ('long', 'V', datetime('now'), NULL, 'failed: OSError')")
    c.commit()
    assert "failed: OSError" in watchdog.malayalam_missing(str(tmp_path / "a.db"))
    c.execute("UPDATE jobs SET ml_video_id = 'M'")
    c.commit()
    assert watchdog.malayalam_missing(str(tmp_path / "a.db")) is None
