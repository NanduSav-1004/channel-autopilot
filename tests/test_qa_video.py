import shutil
import subprocess

import pytest

from autopilot import qa_video as q

OK_INFO = {"video": {"codec_type": "video"}, "audio": {"codec_type": "audio"}, "v_dur": 300.0, "a_dur": 300.1, "dur": 300.1, "size": (1280, 720)}
NONE = {"black": [], "freeze": [], "silence": [], "silence_open": []}


def test_a_healthy_video_passes_and_each_fault_is_named():
    ok = q.judge(OK_INFO, NONE, (-14.4, -1.5), "long", (1280, 720))
    assert ok["errors"] == [] and ok["warnings"] == []
    assert q.judge({**OK_INFO, "audio": None}, NONE, None, "long", None)["errors"] == ["no sound stream"]
    assert "frame size" in q.judge(OK_INFO, NONE, None, "long", (1920, 1080))["errors"][0]
    assert q.judge({**OK_INFO, "a_dur": 296.0}, NONE, None, "long", None)["errors"]                      # 4 s apart
    assert q.judge({**OK_INFO, "a_dur": 301.5}, NONE, None, "long", None)["warnings"]                    # 1.5 s apart: only noted
    assert q.judge({**OK_INFO, "v_dur": 60.0, "a_dur": 60.0, "dur": 60.0}, NONE, None, "long", None)["errors"]   # far too short for a long video
    assert q.judge({**OK_INFO, "v_dur": 70.0, "a_dur": 70.0, "dur": 70.0}, NONE, None, "short", None)["errors"]  # too long for a Short


def test_black_frozen_and_silent_stretches_are_errors_only_when_long_and_not_at_the_edges():
    fade_in_out = {**NONE, "black": [(0.0, 0.8), (299.0, 300.1)], "silence": [(298.0, 300.1)]}
    assert q.judge(OK_INFO, fade_in_out, None, "long", None)["errors"] == []                             # fades at the ends are normal
    assert q.judge(OK_INFO, {**NONE, "black": [(100.0, 100.7)]}, None, "long", None)["warnings"]
    dark_scene = q.judge(OK_INFO, {**NONE, "black": [(132.0, 134.7), (200.0, 203.7)]}, None, "long", None)          # a bulb that begins to glow
    assert dark_scene["warnings"] and not dark_scene["errors"]
    assert q.judge(OK_INFO, {**NONE, "black": [(100.0, 109.0)]}, None, "long", None)["errors"]
    assert q.judge({**OK_INFO, "v_dur": 40.0, "a_dur": 40.0, "dur": 40.0}, {**NONE, "black": [(10.0, 17.0)]}, None, "short", None)["errors"]
    assert q.judge(OK_INFO, {**NONE, "freeze": [(50.0, 58.0)]}, None, "long", None) ["warnings"] and not q.judge(OK_INFO, {**NONE, "freeze": [(50.0, 58.0)]}, None, "long", None)["errors"]
    assert q.judge(OK_INFO, {**NONE, "freeze": [(50.0, 70.0)]}, None, "long", None)["errors"]
    assert q.judge(OK_INFO, {**NONE, "silence": [(100.0, 104.0)]}, None, "long", None)["warnings"]
    assert q.judge(OK_INFO, {**NONE, "silence": [(100.0, 110.0)]}, None, "long", None)["errors"]
    loud = q.judge(OK_INFO, NONE, (-22.0, -0.2), "long", None)
    assert len(loud["warnings"]) == 2 and not loud["errors"]


@pytest.mark.skipif(not (shutil.which("ffmpeg") and shutil.which("ffprobe")), reason="needs ffmpeg")
def test_the_real_scan_finds_black_picture_and_dead_silence_in_a_made_up_clip(tmp_path):
    clip = tmp_path / "bad.mp4"
    # 30 s of moving picture with a 4 s black stretch at 10 s, and a tone that goes silent from 15 s to 25 s
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc2=s=320x180:r=24:d=30", "-f", "lavfi", "-i", "sine=f=300:d=30",
                    "-filter_complex", ("[0:v]drawbox=x=0:y=0:w=320:h=180:color=black:t=fill:enable='between(t,10,14)'[v];"
                                        "[1:a]volume=enable='between(t,15,25)':volume=0[a]"), "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", str(clip)], check=True)
    found = q.scan(clip)
    assert any(abs(a - 10) < 0.6 and abs(b - 14) < 0.6 for a, b in found["black"])
    assert any(abs(a - 15) < 0.6 for a, b in found["silence"])
    res = q.judge(q.probe(clip), found, q.loudness(clip), "short", (320, 180))
    assert any("black" in e for e in res["errors"]) and any("silence" in e for e in res["errors"])
    with pytest.raises(q.VideoCheckError):
        q.gate(clip, "short", (320, 180), log=lambda m: None)


@pytest.mark.skipif(not (shutil.which("ffmpeg") and shutil.which("ffprobe")), reason="needs ffmpeg")
def test_a_missing_or_unreadable_file_never_raises_from_the_check_itself(tmp_path):
    logs = []
    out = q.gate(tmp_path / "nothing.mp4", "short", None, log=logs.append)
    assert out["errors"] == [] and "could not check" in logs[0]
