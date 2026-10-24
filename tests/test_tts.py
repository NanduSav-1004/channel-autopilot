

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
