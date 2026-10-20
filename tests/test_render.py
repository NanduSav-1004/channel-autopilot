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
