import wave

import numpy as np

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
