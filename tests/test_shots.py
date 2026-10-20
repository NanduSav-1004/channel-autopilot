import itertools

from autopilot.commons import license_ok, parse_results
from autopilot.shots import plan_shots


def test_plan_shots_covers_every_frame_without_gaps():
    timings = [{"start": 0.0, "end": 31.37}, {"start": 31.37, "end": 77.9}]
    plan = plan_shots(timings, fps=24)
    spans = [s for sec in plan for s in sec]
    assert spans[0][0] == 0 and spans[-1][1] == round(77.9 * 24)
    assert all(a[1] == b[0] for a, b in itertools.pairwise(spans))


def test_license_filter():
    assert license_ok("CC BY-SA 4.0") and license_ok("CC0") and license_ok("Public domain")
    assert not license_ok("CC BY-NC 4.0") and not license_ok("CC BY-ND 2.0") and not license_ok("")


def _page(lic, w=2000, h=1000, mime="image/jpeg"):
    return {"title": "File:x.jpg", "imageinfo": [{"mime": mime, "width": w, "height": h, "url": "u",
            "thumburl": "t", "descriptionurl": "d", "extmetadata": {"LicenseShortName": {"value": lic},
            "Artist": {"value": "<b>Ann</b>"}}}]}


def test_parse_results_filters_license_size_and_aspect():
    data = {"query": {"pages": [_page("CC BY 4.0"), _page("CC BY-NC 4.0"), _page("CC0", w=500, h=300),
                                 _page("CC0", w=1000, h=1500), _page("CC0", mime="image/svg+xml")]}}
    out = parse_results(data)
    assert len(out) == 1 and out[0]["artist"] == "Ann"
