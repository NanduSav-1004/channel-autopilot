import shutil
import wave

import numpy as np
import pytest

from autopilot.audio import RATE, generate_ambient


def test_ambient_has_requested_length_and_headroom(tmp_path):
    p = generate_ambient(20, tmp_path / "a.wav", seed=1)
    with wave.open(str(p)) as w:
        assert abs(w.getnframes() / RATE - 20) < 0.01
        data = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2")
    assert data.max() < 32767 * 0.85 and np.abs(data).mean() > 500  # audible, not clipped


def test_ambient_is_deterministic_per_seed_and_varies_across_seeds(tmp_path):
    a = generate_ambient(5, tmp_path / "a.wav", seed=2).read_bytes()
    b = generate_ambient(5, tmp_path / "b.wav", seed=2).read_bytes()
    c = generate_ambient(5, tmp_path / "c.wav", seed=3).read_bytes()
    assert a == b and a != c


def test_moods_change_the_colour_but_not_the_length_and_plain_is_untouched(tmp_path):
    import numpy as np

    from autopilot import audio

    def load(p):
        import wave

        with wave.open(str(p)) as w:
            return np.frombuffer(w.readframes(w.getnframes()), dtype="<i2")

    plain = load(audio.generate_ambient(20, tmp_path / "p.wav", seed=3))
    same = load(audio.generate_ambient(20, tmp_path / "p2.wav", seed=3, mood="plain"))
    cur = load(audio.generate_ambient(20, tmp_path / "c.wav", seed=3, mood="curious"))
    mys = load(audio.generate_ambient(20, tmp_path / "m.wav", seed=3, mood="mysterious"))
    assert (plain == same).all()                                       # the pad itself is made exactly as before
    assert len(cur) == len(mys) == len(plain)
    assert not (cur == plain).all() and not (mys == plain).all() and not (cur == mys).all()
    assert np.abs(cur).max() < 32767 * 0.81 and np.abs(mys).max() < 32767 * 0.81      # same loudness ceiling: no clipping


def test_mood_is_picked_from_the_topic_and_can_be_switched_off():
    from autopilot import audio
    from autopilot.config import Config, music_mood

    assert [audio.mood_for_category(c) for c in ("space", "what_if", "core", "history", None, "unknown")] == \
        ["mysterious", "mysterious", "curious", "plain", "curious", "curious"]
    assert [audio.mood_for_theme(t) for t in ("housing", "food", "uk", None)] == ["mysterious", "curious", "plain", "plain"]
    on = Config(niche="n", audience="a", formats={}, audio={"music_moods": True})
    assert music_mood(on, "space") == "mysterious" and music_mood(Config(niche="n", audience="a", formats={}), "space") == "plain"


def _tone(path, seconds, amp):
    import wave

    import numpy as np

    t = np.arange(int(48000 * seconds)) / 48000
    x = amp * (np.sin(2 * np.pi * 220 * t) + 0.5 * np.sin(2 * np.pi * 1330 * t)) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * t))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="needs ffmpeg")
def test_master_loudness_brings_a_quiet_or_a_hot_mix_to_the_target_and_never_clips(tmp_path):
    from autopilot import render

    for name, amp in (("quiet", 0.04), ("hot", 0.95)):
        wav = tmp_path / f"{name}.wav"
        _tone(wav, 20, amp)
        assert render.master_loudness(wav, log=lambda m: None)
        m = render.measure_loudness(wav)
        assert abs(float(m["input_i"]) - render.FINAL_LUFS) <= 2.0, (name, m)
        assert float(m["input_tp"]) <= render.FINAL_TP + 0.3, (name, m)


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="needs ffmpeg")
def test_master_loudness_leaves_silence_and_broken_files_alone(tmp_path):
    from autopilot import render

    silent = tmp_path / "s.wav"
    _tone(silent, 5, 0.0)
    before = silent.read_bytes()
    assert render.master_loudness(silent, log=lambda m: None) is False and silent.read_bytes() == before
    bad = tmp_path / "bad.wav"
    bad.write_bytes(b"not audio")
    assert render.master_loudness(bad, log=lambda m: None) is False and bad.read_bytes() == b"not audio"
