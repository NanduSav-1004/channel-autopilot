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
