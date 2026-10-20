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
