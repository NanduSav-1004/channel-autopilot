

def test_a_narration_is_never_split_across_gemini_models(tmp_path):
    """The same voice name sounds different on different models: a model that runs out partway means the WHOLE narration
    is redone with the next model."""
    import numpy as np

    from autopilot import tts

    class Fake:
        name = "gemini"
        whole_section = True

        def __init__(self, models, die_after=None):
            self.models, self.die_after, self.calls = models, die_after, 0

        def variants(self):
            return [Fake([m], die_after=1 if m == "m1" else None) for m in self.models]

        def synth_section(self, sentences):
            self.calls += 1
            if self.die_after is not None and self.calls > self.die_after:
                raise OSError("quota")
            used.append(self.models[0])
            pcm = (np.zeros(24000, dtype="<i2")).tobytes()
            return pcm, 24000, [(0.0, 0.5)] * len(sentences)

    used: list[str] = []
    script = {"sections": [{"heading": "a", "narration": "One. Two."}, {"heading": "b", "narration": "Three. Four."}]}
    timings = tts.synthesize_script(script, tmp_path / "n.wav", Fake(["m1", "m2"]))
    assert len(timings) == 2
    assert used[-2:] == ["m2", "m2"]          # the final narration is entirely from the second model


def _tone_pcm(seconds, rate=24000, amp=8000, hz=220):
    import numpy as np

    t = np.arange(int(seconds * rate)) / rate
    return (np.sin(2 * np.pi * hz * t) * amp).astype("<i2")


def test_a_noise_burst_after_the_last_word_is_cut():
    import numpy as np

    from autopilot import tts

    rate = 24000
    rng = np.random.default_rng(1)
    speech = np.concatenate([_tone_pcm(2.0), np.zeros(int(0.3 * rate), dtype="<i2"), _tone_pcm(1.5)])
    burst = (rng.normal(0, 12000, int(0.14 * rate))).astype("<i2")                 # a short loud hiss after a pause
    audio = np.concatenate([speech, np.zeros(int(0.25 * rate), dtype="<i2"), burst]).tobytes()
    out, cut = tts.trim_tail_artifact(audio, rate)
    assert cut > 0.2 and len(out) / 2 / rate < len(speech) / rate + 0.2


def test_a_real_last_word_and_attached_endings_are_kept():
    import numpy as np

    from autopilot import tts

    rate = 24000
    pause = np.zeros(int(0.3 * rate), dtype="<i2")
    audio = np.concatenate([_tone_pcm(2.0), pause, _tone_pcm(1.5)]).tobytes()          # ends on speech
    assert tts.trim_tail_artifact(audio, rate)[1] == 0.0
    attached = np.concatenate([_tone_pcm(2.0), np.zeros(int(0.05 * rate), dtype="<i2"), _tone_pcm(0.2, amp=3000)]).tobytes()
    assert tts.trim_tail_artifact(attached, rate)[1] == 0.0                              # no real pause: part of the word


def test_fade_out_ends_in_silence_without_changing_the_length():
    import numpy as np

    from autopilot import tts

    pcm = _tone_pcm(1.0).tobytes()
    out = tts.fade_out(pcm, 24000)
    a = np.frombuffer(out, dtype="<i2")
    assert len(out) == len(pcm) and abs(int(a[-1])) < 100 and np.abs(a[:12000]).max() > 7000


def test_word_times_that_are_squeezed_or_far_from_their_sentence_are_rejected():
    from autopilot import tts

    ok = tts.estimate_word_times("one two three four five six", 10.0, 13.0)
    assert not tts.words_look_wrong(ok, 10.0, 13.0)
    squeezed = [{"w": "w", "s": 12.90 + i * 0.01, "e": 12.91 + i * 0.01} for i in range(6)]       # a burst at the very end
    assert tts.words_look_wrong(squeezed, 10.0, 13.0)
    late = [{"w": "w", "s": 14.0 + i * 0.4, "e": 14.3 + i * 0.4} for i in range(4)]                 # a long empty lead-in
    assert tts.words_look_wrong(late, 10.0, 16.0)
    hole = ok[:3] + [{**w, "s": w["s"] + 2.0, "e": w["e"] + 2.0} for w in ok[3:]]
    assert tts.words_look_wrong(hole, 10.0, 16.0)
    assert not tts.words_look_wrong(ok[:1], 10.0, 13.0)


def test_a_broken_whisper_refinement_falls_back_to_an_even_spread(tmp_path):
    import wave

    import numpy as np

    from autopilot import tts

    wav = tmp_path / "n.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(24000)
        w.writeframes(np.zeros(24000 * 6, dtype="<i2").tobytes())
    timings = [{"heading": "h", "start": 0.0, "end": 6.0,
                "sentences": [{"text": "one two three four five six", "start": 0.0, "end": 6.0}]}]
    late = [{"word": w, "start": 5.9 + i * 0.01, "end": 5.91 + i * 0.01} for i, w in enumerate(["one", "two", "three", "four", "five", "six"])]
    tts.add_word_times(wav, timings, whisper=lambda b: late)           # Whisper "heard" every word in the last instants
    words = timings[0]["sentences"][0]["words"]
    assert not tts.words_look_wrong(words, 0.0, 6.0) and words[0]["s"] < 0.5 and words[-1]["e"] <= 6.0
