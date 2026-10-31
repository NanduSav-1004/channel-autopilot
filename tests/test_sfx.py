import wave

import numpy as np
import pytest

from autopilot import sfx


def _wav(path, x):
    sfx._write(path, x)
    return path


def test_every_sound_is_a_clean_short_signal_without_clipping():
    for name in ("tick0", "tick4", "pop", "accent", "whoosh", "shimmer", "swish:1.5"):
        s = sfx._sound(name)
        assert 0.02 < len(s) / sfx.RATE < 2.0 and np.isfinite(s).all() and 0.3 < np.abs(s).max() <= 1.0


def test_events_follow_each_charts_animation_and_stay_inside_the_scene():
    counter = sfx.events_for({"type": "counter", "duration": 5.0, "badge": "+3%"})
    assert sum(1 for e in counter if e[1].startswith("tick")) == 16 and ("pop" in [e[1] for e in counter])
    assert sfx.events_for({"type": "title", "duration": 4.0}) == [(0.18, "accent", 0.9)]            # text cards: one soft accent
    assert [e for e in sfx.events_for({"type": "counter", "duration": 1.2}) if e[0] >= 1.1] == []     # nothing after the scene has ended
    bars = sfx.events_for({"type": "bars", "duration": 6.0, "items": [{}, {}, {}]})
    assert [e[1] for e in bars].count("tick2") == 3


def test_a_run_of_short_scenes_does_not_get_a_whoosh_each():
    specs = [{"type": "line", "duration": 1.5, "draw": 1.0}] * 4
    ev = sfx.track_events(specs, [0.0, 1.5, 3.0, 4.5])
    assert [e for e in ev if e[1] == "whoosh"] == [(0.0, "whoosh", 0.55), (3.0, "whoosh", 0.55)]


def test_track_and_mix_keep_the_voice_and_never_clip(tmp_path):
    voice_mix = _wav(tmp_path / "mix.wav", 0.6 * np.sin(2 * np.pi * 220 * np.arange(sfx.RATE * 4) / sfx.RATE))
    track = sfx.render_track([(0.5, "pop", 1.0), (1.0, "accent", 1.0), (2.0, "whoosh", 1.0)], 4.0, tmp_path / "sfx.wav")
    out = sfx.add_to_mix(voice_mix, track, tmp_path / "out.wav")
    a, b = sfx._read(voice_mix), sfx._read(out)
    assert len(a) == len(b) and np.abs(b).max() <= 0.97 + 1e-3
    assert np.abs(b - a).max() < 0.3                                                       # the effects are quiet next to the voice
    with wave.open(str(track)) as w:
        assert w.getframerate() == sfx.RATE and w.getnchannels() == 1
    loud = _wav(tmp_path / "loud.wav", 0.99 * np.ones(sfx.RATE))
    big = sfx.render_track([(0.1, "accent", 1.0)], 1.0, tmp_path / "s2.wav")
    assert np.abs(sfx._read(sfx.add_to_mix(loud, big, tmp_path / "o2.wav"))).max() <= 0.97 + 1e-3


@pytest.mark.parametrize("typ", ["title", "line", "multiline", "stacked", "counter", "compare", "bars", "slope", "race", "kpi", "waffle", "gauge", "donut", "heatmap", "map",
                                 "world_map", "scatter"])
def test_every_chart_type_has_a_sound_plan(typ):
    ev = sfx.events_for({"type": typ, "duration": 8.0, "items": [{}] * 5, "cards": [{}] * 3, "draw": 4.0})
    assert ev and all(0 <= e[0] < 8.0 and 0 < e[2] <= 1 for e in ev)
    sfx.render_track([(e[0], e[1], e[2]) for e in ev], 9.0, __import__("pathlib").Path("/tmp") / f"sfx_test_{typ}.wav")
