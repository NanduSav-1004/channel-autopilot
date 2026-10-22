import shutil
import subprocess
import wave

import numpy as np
import pytest

from autopilot import music, stages, tts
from autopilot.config import Config


class FakeEngine:
    """1 s of audio per sentence at 8 kHz."""
    name = "fake"

    def synth(self, text):
        return b"\x01\x00" * 8000, 8000


def test_synthesize_script_with_any_engine_gives_exact_sentence_timings(tmp_path):
    script = {"sections": [{"heading": "A", "narration": "One two. Three four."}, {"heading": "B", "narration": "Five six."}]}
    timings = tts.synthesize_script(script, tmp_path / "n.wav", FakeEngine())
    s = timings[0]["sentences"]
    assert s[0]["start"] == 0 and s[0]["end"] == pytest.approx(1.0)
    assert s[1]["start"] == pytest.approx(1.0 + tts.SENTENCE_PAUSE)
    assert timings[1]["start"] == pytest.approx(timings[0]["end"])
    with wave.open(str(tmp_path / "n.wav")) as w:
        assert w.getframerate() == 8000 and w.getnframes() / 8000 == pytest.approx(timings[-1]["end"], abs=0.01)


def test_make_engine_falls_back_to_piper_when_kokoro_is_unavailable(monkeypatch, capsys):
    class Boom:
        def __init__(self, *a, **k):
            raise OSError("model file missing")

    class FakePiper:
        name = "piper"

    monkeypatch.setattr(tts, "KokoroEngine", Boom)
    monkeypatch.setattr(tts, "PiperEngine", FakePiper)
    assert tts.make_engine({"voice_engine": "kokoro"}).name == "piper"
    assert "falling back to Piper" in capsys.readouterr().out
    assert tts.make_engine({}).name == "piper"  # default stays Piper until config says otherwise


def test_make_engine_uses_kokoro_settings(monkeypatch):
    seen = {}

    class FakeKokoro:
        name = "kokoro"

        def __init__(self, voice, speed):
            seen.update(voice=voice, speed=speed)

    monkeypatch.setattr(tts, "KokoroEngine", FakeKokoro)
    assert tts.make_engine({"voice_engine": "kokoro", "voice_name": "am_michael", "voice_speed": 1.2}).name == "kokoro"
    assert seen == {"voice": "am_michael", "speed": 1.2}


@pytest.mark.parametrize("style", sorted(music.STYLES))
def test_beat_music_has_requested_length_headroom_and_energy(tmp_path, style):
    p = music.generate_beat(12, tmp_path / "m.wav", seed=1, style=style)
    with wave.open(str(p)) as w:
        assert abs(w.getnframes() / music.RATE - 12) < 0.01
        x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2") / 32768
    assert np.abs(x).max() < 0.9 and np.sqrt((x ** 2).mean()) > 0.05  # audible and not clipped


def test_beat_music_is_deterministic_per_seed_and_varies_by_seed_and_style(tmp_path):
    a = music.generate_beat(6, tmp_path / "a.wav", seed=2, style="upbeat").read_bytes()
    assert a == music.generate_beat(6, tmp_path / "b.wav", seed=2, style="upbeat").read_bytes()
    assert a != music.generate_beat(6, tmp_path / "c.wav", seed=3, style="upbeat").read_bytes()
    assert a != music.generate_beat(6, tmp_path / "d.wav", seed=2, style="lofi").read_bytes()


def test_stage_picks_beat_or_ambient_music_from_config(tmp_path, monkeypatch):
    import sqlite3

    calls = []
    monkeypatch.setattr(stages.music, "generate_beat", lambda s, o, seed, style: calls.append(("beat", style)) or o)
    monkeypatch.setattr(stages.audio, "generate_ambient", lambda s, o, seed: calls.append(("ambient",)) or o)
    conn = sqlite3.connect(":memory:")
    for settings, expect in (({"music_style": "pulse"}, ("beat", "pulse")), ({}, ("ambient",)), ({"music_style": "ambient"}, ("ambient",))):
        cfg = Config(niche="s", audience="en", formats={}, audio=settings)
        stages.Stages(conn, cfg, root=tmp_path, work=tmp_path).make_music(tmp_path / "m.wav", 5, 1)
        assert calls[-1] == expect


@pytest.mark.skipif(not (shutil.which("ffmpeg") and shutil.which("ffprobe")), reason="needs ffmpeg")
def test_final_pass_with_music_produces_video_with_balanced_audio(tmp_path):
    from autopilot.render import _final_pass, write_ass

    music.generate_beat(6, tmp_path / "music.wav", seed=1, style="upbeat")
    with wave.open(str(tmp_path / "nar.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(22050)
        t = np.arange(22050 * 4) / 22050
        w.writeframes((np.sin(2 * np.pi * 220 * t) * 0.3 * 32767).astype("<i2").tobytes())
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "color=c=navy:s=320x180:d=4:r=24", "-pix_fmt", "yuv420p", str(tmp_path / "v.mp4")], check=True)
    (tmp_path / "clips.txt").write_text("file 'v.mp4'\n")
    write_ass([{"heading": "h", "start": 0, "end": 4, "sentences": [{"text": "Hi there.", "start": 0, "end": 2}]}], tmp_path / "c.ass")
    out = tmp_path / "out.mp4"
    _final_pass(tmp_path / "clips.txt", tmp_path / "nar.wav", tmp_path / "c.ass", out, tmp_path / "music.wav")
    info = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(out)], capture_output=True, text=True, check=True).stdout
    assert "audio" in info and "video" in info
    # measure the loudness actually delivered: the mix must land near the -16 LUFS target (and not clip)
    r = subprocess.run(["ffmpeg", "-i", str(out), "-af", "ebur128=peak=true", "-f", "null", "-"], check=False, capture_output=True, text=True)
    lufs = float(r.stderr.split("I:")[-1].split("LUFS")[0])
    assert -22 < lufs < -11
