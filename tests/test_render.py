import itertools
import shutil
import subprocess

import pytest

from autopilot.render import _ass_time, write_ass
from autopilot.tts import split_sentences


def test_split_sentences_keeps_abbreviation_free_boundaries():
    assert split_sentences("One. Two! Three? four.") == ["One.", "Two!", "Three? four."]


def test_ass_time_format():
    assert _ass_time(3725.5) == "1:02:05.50"


def test_write_ass_has_one_event_per_sentence(tmp_path):
    timings = [{"heading": "h", "start": 0, "end": 3,
                "sentences": [{"text": "Hi {x}.", "start": 0, "end": 1}, {"text": "Yo.", "start": 1, "end": 2}]}]
    p = tmp_path / "c.ass"
    write_ass(timings, p)
    body = p.read_text()
    assert body.count("Dialogue:") == 2 and "{x}" not in body


# ---------- word-by-word captions ----------
def _w(text, s, e):
    return {"w": text, "s": s, "e": e}


def test_caption_groups_break_at_sentence_ends_commas_and_size_without_orphans():
    from autopilot.render import caption_groups

    words = [_w(x, i * 0.3, i * 0.3 + 0.25) for i, x in enumerate(["In", "1937,", "Olaf", "Stapledon", "described", "a", "gauze", "of", "light-traps."])]
    groups = [[w["w"] for w in g] for g in caption_groups(words, 3)]
    assert groups[0] == ["In", "1937,"] and groups[-1][-1] == "light-traps."
    assert all(len(g) <= 4 for g in groups) and all(len(g) >= 2 for g in groups)  # a lone last word is merged back
    assert caption_groups([], 3) == []


def test_word_captions_highlight_one_word_at_a_time_and_follow_the_voice(tmp_path):
    from autopilot.render import HILITE, LONG_CAPTIONS, SHORT_CAPTIONS, write_ass_words

    sent = {"text": "Dyson began it.", "start": 1.0, "end": 2.2,
            "words": [_w("Dyson", 1.0, 1.4), _w("began", 1.45, 1.8), _w("it.", 1.85, 2.2)]}
    timings = [{"heading": "h", "start": 0, "end": 3, "sentences": [sent]}]
    short, longp = tmp_path / "s.ass", tmp_path / "l.ass"
    write_ass_words(timings, short, SHORT_CAPTIONS)
    write_ass_words(timings, longp, LONG_CAPTIONS)
    events = [ln for ln in short.read_text().splitlines() if ln.startswith("Dialogue")]
    assert len(events) == 3                                                    # one event per word
    assert "0:00:01.00" in events[0] and "0:00:01.45" in events[1]             # starts exactly when the word starts
    assert events[0].count(HILITE) == 1 and f"{{\\c{HILITE}&}}DYSON" in events[0] and "BEGAN" in events[0]  # uppercase, one amber
    assert "PlayResY: 1920" in short.read_text() and "PlayResY: 720" in longp.read_text()
    assert "Dyson" in longp.read_text()                                        # long videos keep normal case


def test_word_captions_estimate_words_when_a_sentence_has_none_and_escape_braces(tmp_path):
    from autopilot.render import LONG_CAPTIONS, write_ass_words

    timings = [{"heading": "h", "start": 0, "end": 3, "sentences": [{"text": "Old {job} without words.", "start": 0.0, "end": 2.0}]}]
    p = tmp_path / "a.ass"
    write_ass_words(timings, p, LONG_CAPTIONS)
    body = p.read_text()
    assert body.count("Dialogue:") >= 3 and "{job}" not in body and "(job)" in body


def test_word_captions_never_overlap_or_run_backwards(tmp_path):
    from autopilot.render import SHORT_CAPTIONS, write_ass_words

    words = [_w(f"w{i}", i * 0.2, i * 0.2 + 0.18) for i in range(9)]
    timings = [{"heading": "h", "start": 0, "end": 3, "sentences": [{"text": " ".join(w["w"] for w in words), "start": 0.0, "end": 1.8, "words": words}]}]
    p = tmp_path / "a.ass"
    write_ass_words(timings, p, SHORT_CAPTIONS)

    def secs(ts):
        h, m, s = ts.split(":")
        return int(h) * 3600 + int(m) * 60 + float(s)

    spans = [(secs(ln.split(",")[1]), secs(ln.split(",")[2])) for ln in p.read_text().splitlines() if ln.startswith("Dialogue")]
    assert all(e > s for s, e in spans) and all(a[1] <= b[0] + 0.05 for a, b in itertools.pairwise(spans))


@pytest.mark.skipif(not (shutil.which("ffmpeg") and shutil.which("ffprobe")), reason="needs ffmpeg")
def test_render_photo_video_cuts_fast_and_reuses_media_end_to_end(tmp_path):
    import wave

    import numpy as np
    from PIL import Image

    from autopilot.render import render_photo_video
    from autopilot.shots import plan_cuts

    imgs = []
    for i, colour in enumerate(((200, 40, 40), (40, 200, 40))):
        p = tmp_path / f"i{i}.jpg"
        Image.new("RGB", (1280, 720), colour).save(p)
        imgs.append({"kind": "image", "path": p})
    nar = tmp_path / "n.wav"
    with wave.open(str(nar), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(22050)
        w.writeframes(np.zeros(22050 * 14, dtype="<i2").tobytes())
    words = [{"w": "word", "s": 0.5 + k * 1.0, "e": 0.9 + k * 1.0} for k in range(12)]
    timings = [{"heading": "A", "start": 0.0, "end": 14.0, "sentences": [{"text": "word " * 12, "start": 0.4, "end": 13.0, "words": words}]}]
    plan = plan_cuts(timings, [2])
    assert len(plan[0]) == 4                       # 14 s at one cut per 3.5 s, with 2 images each used twice
    out = tmp_path / "v.mp4"
    render_photo_video({"title": "T"}, timings, [imgs], plan, nar, out, tmp_path / "w")
    info = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height:format=duration", "-of", "default=nw=1", str(out)],
                          capture_output=True, text=True, check=True).stdout
    assert "width=1280" in info and 13.5 < float(info.split("duration=")[1]) < 14.6
