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
