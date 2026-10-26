

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
