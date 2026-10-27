import shutil
import subprocess
import wave

import numpy as np
import pytest

from autopilot import mascot


def _wav(path, parts, rate=24000):
    pcm = np.concatenate([np.full(int(rate * s), a, dtype="<i2") * (np.sin(np.arange(int(rate * s)) / 20) > -2) for s, a in parts])
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm.astype("<i2").tobytes())


def test_the_mouth_opens_with_the_voice_and_closes_in_silence(tmp_path):
    p = tmp_path / "n.wav"
    _wav(p, [(1.0, 0), (1.0, 9000), (1.0, 0), (1.0, 2500)])
    lv = mascot.mouth_levels(p, fps=12)
    assert len(lv) == 48 and max(lv[:9]) == 0 and max(lv[14:22]) >= 2 and max(lv[28:34]) == 0 and 1 <= max(lv[38:46]) <= 3


def test_the_sprites_differ_by_mouth_and_blink_and_are_transparent():
    a, b, c = mascot.sprite(120, 0, False), mascot.sprite(120, 3, False), mascot.sprite(120, 0, True)
    assert a.size == (120, 120) and a.getpixel((2, 2))[3] == 0
    assert a.tobytes() != b.tobytes() and a.tobytes() != c.tobytes()


def test_blinks_are_occasional_and_repeatable():
    f = mascot.blink_frames(12 * 60)
    assert 5 <= len(f) // 2 <= 30 and f == mascot.blink_frames(12 * 60)


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="needs ffmpeg")
def test_the_track_is_a_transparent_video_as_long_as_the_narration(tmp_path):
    p = tmp_path / "n.wav"
    _wav(p, [(1.0, 8000), (1.0, 0)])
    out = mascot.render_track(p, tmp_path / "m.mov", size=100)
    info = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,pix_fmt,width,height:format=duration",
                           "-of", "default=nw=1", str(out)], capture_output=True, text=True, check=True).stdout
    assert "qtrle" in info and "width=108" in info and 1.8 < float(info.split("duration=")[1]) < 2.2


def test_the_config_decides_which_videos_get_which_mascot():
    from autopilot.config import Config, mascot_style

    def cfg(**render):
        return Config(niche="s", audience="a", formats={}, render=render)

    assert mascot_style(cfg(), True) is None and mascot_style(cfg(mascot=False), True) is None
    assert mascot_style(cfg(mascot="shorts", mascot_style="atom"), True) == "atom"
    assert mascot_style(cfg(mascot="shorts", mascot_style="atom"), False) is None          # shorts only: long videos untouched
    assert mascot_style(cfg(mascot="all"), False) == "bulb" and mascot_style(cfg(mascot="shorts", mascot_style="nope"), True) == "bulb"


def test_the_atom_sprites_differ_and_the_electrons_move():
    a, b = mascot.sprite(120, 0, False, "atom", 0), mascot.sprite(120, 0, False, "atom", 7)
    assert a.size == (120, 120) and a.tobytes() != b.tobytes()
    assert a.tobytes() != mascot.sprite(120, 0, False, "bulb").tobytes()


def _tiny_render(tmp_path, mascot_arg):
    from PIL import Image

    from autopilot.render import render_short

    img = tmp_path / "i.jpg"
    Image.new("RGB", (1280, 720), (30, 80, 160)).save(img)
    nar = tmp_path / "n.wav"
    _wav(nar, [(2.0, 8000), (1.0, 0), (2.0, 6000)])
    words = [{"w": "word", "s": 0.3 + k * 0.4, "e": 0.6 + k * 0.4} for k in range(10)]
    timings = [{"heading": "A", "start": 0.0, "end": 5.0,
                "sentences": [{"text": "word " * 10, "start": 0.3, "end": 4.6, "words": words}]}]
    out = tmp_path / f"s_{mascot_arg}.mp4"
    render_short({"title": "T"}, timings, [{"kind": "image", "path": img}], nar, out, tmp_path / f"w_{mascot_arg}", mascot=mascot_arg)
    return out


def _durations(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout.split()
    return {line.split(",")[0]: float(line.split(",")[1]) for line in out}


@pytest.mark.skipif(not (shutil.which("ffmpeg") and shutil.which("ffprobe")), reason="needs ffmpeg")
def test_the_mascot_does_not_change_the_length_or_the_audio_video_sync(tmp_path):
    plain, with_bulb, with_atom = (_tiny_render(tmp_path, m) for m in (None, "bulb", "atom"))
    base = _durations(plain)
    for out in (with_bulb, with_atom):
        d = _durations(out)
        assert abs(d["video"] - base["video"]) < 0.05 and abs(d["audio"] - base["audio"]) < 0.05
        assert abs(d["video"] - d["audio"]) < 0.1


@pytest.mark.skipif(not (shutil.which("ffmpeg") and shutil.which("ffprobe")), reason="needs ffmpeg")
def test_a_broken_mascot_never_stops_the_video_from_rendering(tmp_path, monkeypatch):
    def boom(*a, **k):
        raise OSError("mascot exploded")

    monkeypatch.setattr(mascot, "render_track", boom)
    out = _tiny_render(tmp_path, "bulb")
    assert out.exists() and out.stat().st_size > 5_000
