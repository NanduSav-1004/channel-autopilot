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
              "sections": [{"heading": "H1", "narration": "N1"}, {"heading": "H2", "narration": "N2"}]}
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
