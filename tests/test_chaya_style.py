import numpy as np

from autopilot import chaya_sound as cs

SPEC = {"duration": 30.0, "beats": [0.5, 4.0, 9.0], "cards": [{"t0": 0.6, "t1": 3.5, "ml": "x", "en": "x", "col": "#fff"}],
        "scenes": [{"kind": "compose", "t0": 0.0, "t1": 12.0, "tr": "cut", "p": {"bg": "storm", "layers": [{"t": "particles", "kind": "rain"}, {"t": "bolt", "at": 0.5}]}},
                   {"kind": "stat", "t0": 12.0, "t1": 20.0, "tr": "whip", "p": {}}, {"kind": "outro", "t0": 20.0, "t1": 30.0, "tr": "zoom", "p": {}}]}


def test_sound_plan_has_cuts_risers_thunder_and_a_matching_bed():
    ev, beds = cs.events_for(SPEC)
    names = [n.split(":")[0] for _, n, _ in ev]
    assert {"impact", "whoosh", "riser", "crack", "thunder", "ding", "click", "pop"} <= set(names)
    assert beds and beds[0][2] == "rain"
    assert all(0 <= t < SPEC["duration"] for t, _, _ in ev)


def test_effects_track_is_audible_and_not_clipped(tmp_path):
    out = cs.render(SPEC, tmp_path / "sfx.wav")
    import wave
    with wave.open(str(out)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2") / 32768
    assert 0.1 < np.abs(x).max() < 1.0
