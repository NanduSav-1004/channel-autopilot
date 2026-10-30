import shutil
import subprocess

import pytest

from autopilot import datashots as ds
from autopilot.render import carve_span

NARR = "In 2021 scientists sent 319 terabits per second over 3 000 km. A 4.2 K bath cooled mercury in 1911."


def test_numbers_in_ignores_thousands_separators_and_keeps_decimals():
    assert ds.numbers_in(NARR) == {2021.0, 319.0, 3000.0, 4.2, 1911.0}
    assert ds.numbers_in("1,500 and 44.7%") == {1500.0, 44.7}


def test_a_shot_is_kept_only_if_every_number_was_said():
    ok = {"kind": "number", "title": "t", "items": [{"label": "speed", "value": 319, "unit": "Tb/s"}]}
    assert ds.validate(ok, NARR)["items"][0]["value"] == 319.0
    assert ds.validate({**ok, "items": [{"label": "speed", "value": 320, "unit": "Tb/s"}]}, NARR) is None     # never invented
    bars = {"kind": "bars", "title": "t", "items": [{"label": "a", "value": 4.2, "unit": "K"}, {"label": "b", "value": 319, "unit": "K"}]}
    assert ds.validate(bars, NARR) is not None
    assert ds.validate({**bars, "items": [{"label": "a", "value": 4.2, "unit": "K"}, {"label": "b", "value": 319, "unit": "Tb/s"}]}, NARR) is None
    assert ds.validate({"kind": "timeline", "title": "t", "items": [{"label": "x", "value": 1911, "unit": ""}]}, NARR) is None   # too few events
    assert ds.validate({"kind": "pie", "title": "t", "items": []}, NARR) is None


def test_a_line_chart_needs_its_years_in_the_text_too():
    line = {"kind": "line", "title": "t", "items": [{"label": "1911", "value": 4.2, "unit": ""}, {"label": "2021", "value": 319, "unit": ""},
                                                     {"label": "1999", "value": 3000, "unit": ""}]}
    assert ds.validate(line, NARR) is None
    line["items"][2]["label"] = "2021"
    assert ds.validate(line, NARR) is not None


def test_extraction_survives_a_failing_or_silly_model():
    def boom(prompt):
        raise RuntimeError("down")

    assert ds.extract_shot("h", NARR, boom) is None
    assert ds.extract_shot("h", NARR, lambda p: {"shots": []}) is None
    assert ds.extract_shot("h", NARR, lambda p: "nonsense") is None
    good = {"shots": [{"kind": "number", "title": "t", "items": [{"label": "l", "value": 319, "unit": "Tb/s"}]}]}
    assert ds.extract_shot("h", NARR, lambda p: good)["kind"] == "number"


def test_the_shot_starts_just_before_the_figure_is_spoken():
    shot = {"kind": "number", "title": "t", "items": [{"label": "l", "value": 319.0, "unit": "Tb/s"}]}
    words = [{"w": "sent", "s": 10.0, "e": 10.3}, {"w": "319", "s": 10.6, "e": 11.2}]
    sentences = [{"text": "They sent 319 terabits", "start": 9.8, "end": 12.0, "words": words}]
    assert ds.place_shot(shot, sentences) == {"start": 10.2, "seconds": 6.0}
    assert ds.place_shot({**shot, "items": [{"label": "l", "value": 7.0, "unit": ""}]}, sentences) is None


def test_carving_replaces_only_the_stretch_of_a_cut_the_shot_covers():
    shots = [{"start": 10.0, "seconds": 6.0}]                                         # frames 240..384 at 24 fps
    assert carve_span(0, 100, shots) == [(0, 100, None)]
    assert carve_span(300, 450, shots) == [(300, 384, 0), (384, 450, None)]
    assert carve_span(200, 300, shots) == [(200, 240, None), (240, 300, 0)]
    assert carve_span(250, 380, shots) == [(250, 380, 0)]
    assert carve_span(236, 300, shots) == [(236, 300, 0)]                              # a 4-frame sliver is absorbed


@pytest.mark.skipif(not (shutil.which("ffmpeg") and shutil.which("ffprobe")), reason="needs ffmpeg")
def test_every_kind_renders_a_clip_of_the_requested_length(tmp_path):
    shots = {
        "number": {"kind": "number", "title": "Speed", "items": [{"label": "record", "value": 319, "unit": "Tb/s"}]},
        "bars": {"kind": "bars", "title": "Temps", "items": [{"label": "A", "value": 4.2, "unit": "K"}, {"label": "B", "value": 92, "unit": "K"}]},
        "timeline": {"kind": "timeline", "title": "History", "items": [{"label": f"e{i}", "value": 1900 + 10 * i, "unit": ""} for i in range(4)]},
        "line": {"kind": "line", "title": "Growth", "items": [{"label": str(2000 + 5 * i), "value": 10 + 5 * i, "unit": "%"} for i in range(4)]},
    }
    for kind, shot in shots.items():
        for size in ((640, 360), (360, 640)):
            out = ds.render_shot(shot, size, tmp_path / f"{kind}_{size[0]}.mp4", seconds=1.5)
            info = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height:format=duration", "-of", "default=nw=1", str(out)],
                                  capture_output=True, text=True, check=True).stdout
            assert f"width={size[0]}" in info and 1.3 < float(info.split("duration=")[1]) < 1.8, (kind, size)


def _words(text, t0):
    return [{"w": w, "s": t0 + i * 0.4, "e": t0 + i * 0.4 + 0.3} for i, w in enumerate(text.split())]


def test_shots_for_places_a_shot_per_section_spaces_them_and_survives_failures():
    secs = [
        {"heading": "A", "narration": "Light travels 299792 km every second.",
         "sentences": [{"text": "Light travels 299792 km every second.", "start": 2.0, "end": 6.0, "words": _words("Light travels 299792 km every second.", 2.0)}]},
        {"heading": "B", "narration": "It was 1911 when mercury hit 4.2 K.",
         "sentences": [{"text": "It was 1911 when mercury hit 4.2 K.", "start": 8.0, "end": 12.0, "words": _words("It was 1911 when mercury hit 4.2 K.", 8.0)}]},
        {"heading": "C", "narration": "Then 77 K.",
         "sentences": [{"text": "Then 77 K.", "start": 40.0, "end": 42.0, "words": _words("Then 77 K.", 40.0)}]},
    ]

    def gen(prompt):
        if "SECTION: A" in prompt:
            return {"shots": [{"kind": "number", "title": "Speed of light", "items": [{"label": "per second", "value": 299792, "unit": "km"}]}]}
        if "SECTION: B" in prompt:       # 8 s after A's shot starts: too close, skipped
            return {"shots": [{"kind": "number", "title": "Cold", "items": [{"label": "mercury", "value": 4.2, "unit": "K"}]}]}
        raise RuntimeError("model down")

    rendered = []

    def fake_render(shot, size, out, seconds):
        rendered.append((shot["title"], size))
        return out

    logs = []
    out = ds.shots_for(secs, (1280, 720), __import__("pathlib").Path("/tmp/x"), gen=gen, render=fake_render, log=logs.append)
    assert [s["kind"] for s in out] == ["number"] and rendered == [("Speed of light", (1280, 720))]
    assert out[0]["start"] < 4.0 and out[0]["seconds"] == 6.0


def test_shots_for_never_raises_when_rendering_fails(tmp_path):
    secs = [{"heading": "A", "narration": "It reached 319 Tb/s.",
             "sentences": [{"text": "It reached 319 Tb/s.", "start": 1.0, "end": 3.0, "words": _words("It reached 319 Tb/s.", 1.0)}]}]
    good = {"shots": [{"kind": "number", "title": "Speed", "items": [{"label": "", "value": 319, "unit": "Tb/s"}]}]}

    def boom(*a, **k):
        raise OSError("ffmpeg missing")

    logs = []
    assert ds.shots_for(secs, (1280, 720), tmp_path, gen=lambda p: good, render=boom, log=logs.append) == []
    assert any("skipped" in line for line in logs)


def test_the_config_switch_picks_which_videos_get_data_shots():
    from autopilot.config import Config, data_shots_on

    def cfg(**r):
        return Config(niche="s", audience="a", formats={}, render=r)

    assert not data_shots_on(cfg(), True) and not data_shots_on(cfg(data_shots=False), True)
    assert data_shots_on(cfg(data_shots="shorts"), True) and not data_shots_on(cfg(data_shots="shorts"), False)
    assert data_shots_on(cfg(data_shots="all"), False)


@pytest.mark.skipif(not (shutil.which("ffmpeg") and shutil.which("ffprobe")), reason="needs ffmpeg")
def test_a_short_renders_with_a_data_shot_and_keeps_its_length(tmp_path):
    import wave

    import numpy as np
    from PIL import Image

    from autopilot.render import render_short

    img = tmp_path / "i.jpg"
    Image.new("RGB", (1280, 720), (40, 90, 160)).save(img)
    nar = tmp_path / "n.wav"
    with wave.open(str(nar), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(24000)
        w.writeframes((np.sin(np.arange(24000 * 8) / 20) * 6000).astype("<i2").tobytes())
    words = _words("It reached 319 Tb/s today", 1.0)
    timings = [{"heading": "A", "start": 0.0, "end": 8.0,
                "sentences": [{"text": "It reached 319 Tb/s today", "start": 1.0, "end": 3.5, "words": words}]}]
    shot = {"kind": "number", "title": "Speed", "items": [{"label": "record", "value": 319, "unit": "Tb/s"}]}
    clip = ds.render_shot(shot, (1080, 1920), tmp_path / "s.mp4", seconds=3.0)
    plain, with_shot = tmp_path / "plain.mp4", tmp_path / "with.mp4"
    item = [{"kind": "image", "path": img}]
    render_short({"title": "T"}, timings, item, nar, plain, tmp_path / "w1")
    render_short({"title": "T"}, timings, item, nar, with_shot, tmp_path / "w2", data_shots=[{"start": 1.5, "seconds": 3.0, "clip": clip}])

    def dur(p):
        return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                    capture_output=True, text=True, check=True).stdout)

    assert abs(dur(plain) - dur(with_shot)) < 0.1


def test_rule_based_shot_finds_the_first_figure_with_a_unit_without_any_model():
    s = ds.rule_based_shot("Did you know Jupiter holds a thousand Earths? Its volume is 1,321 times that of Earth. It spins every ten hours.")
    assert s["kind"] == "number" and s["items"][0]["value"] == 1321.0 and s["items"][0]["unit"] == "times" and s["items"][0]["label"] == "volume"
    p = ds.rule_based_shot("Its atmosphere is 76% hydrogen and 24% helium by mass.")
    assert p["items"][0]["value"] == 76.0 and p["items"][0]["unit"] == "%"
    assert ds.rule_based_shot("It has the strongest field in the system. In 1911 it began.") is None      # no figure with a unit


def test_when_the_model_is_out_of_quota_a_rule_based_shot_is_used_and_the_log_says_why():
    from autopilot import llm

    def down(prompt):
        raise llm.LLMError("all LLM models are out of quota or busy")

    narration = "Its volume is 1,321 times that of Earth."
    secs = [{"heading": "Jupiter volume", "narration": narration,
             "sentences": [{"text": narration, "start": 1.0, "end": 4.0, "words": _words(narration, 1.0)}]}]
    logs = []
    out = ds.shots_for(secs, (1080, 1920), __import__("pathlib").Path("/tmp/x"), gen=down, render=lambda s, z, o, seconds: o, log=logs.append)
    assert len(out) == 1 and any("model unavailable" in line and "rule-based" in line for line in logs)
    quiet = []
    ds.shots_for([{**secs[0], "narration": "No figures here at all.", "sentences": secs[0]["sentences"]}], (1080, 1920),
                 __import__("pathlib").Path("/tmp/x"), gen=lambda p: {"shots": []}, render=lambda *a, **k: None, log=quiet.append)
    assert any("no shot for" in line for line in quiet)                    # silence is never the answer
