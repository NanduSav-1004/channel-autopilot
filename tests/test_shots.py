import itertools

import pytest

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


# ---------- faster cuts ----------
def _sections(*durations):
    t, out = 0.0, []
    for d in durations:
        out.append({"start": t, "end": t + d})
        t += d
    return out


def test_plan_cuts_cuts_every_few_seconds_when_there_is_enough_media():
    from autopilot.shots import CUT_SECONDS, plan_cuts

    plan = plan_cuts(_sections(60.0), [20])             # 60 s, plenty of media
    assert len(plan[0]) == round(60 / CUT_SECONDS)
    assert all((b - a) / 24 == pytest.approx(CUT_SECONDS, abs=0.5) for a, b in plan[0])


def test_plan_cuts_never_uses_a_piece_of_media_more_than_max_reuse_times_so_sparse_sections_cut_slower():
    from autopilot.shots import MAX_REUSE, plan_cuts

    plan = plan_cuts(_sections(150.0), [3])              # 150 s but only 3 images
    assert len(plan[0]) == MAX_REUSE * 3
    assert (plan[0][0][1] - plan[0][0][0]) / 24 > 10      # so each shot is long, not a rapid repeat


def test_plan_cuts_uses_slow_title_cards_when_a_section_has_no_media_and_covers_every_frame():
    from autopilot.shots import plan_cuts

    timings = _sections(30.0, 41.37, 12.0)
    plan = plan_cuts(timings, [8, 0, 4])
    spans = [s for sec in plan for s in sec]
    assert spans[0][0] == 0 and spans[-1][1] == round(timings[-1]["end"] * 24)
    assert all(a[1] == b[0] for a, b in itertools.pairwise(spans))   # no gaps, no overlaps, even across sections
    assert len(plan[1]) == round(41.37 / 6)                           # the section with no media: slow cards


def test_cut_choice_varies_the_camera_move_between_first_and_second_use():
    from autopilot.shots import cut_choice

    first = [cut_choice(k, 4) for k in range(4)]
    second = [cut_choice(k, 4) for k in range(4, 8)]
    assert [c[0] for c in first] == [0, 1, 2, 3] == [c[0] for c in second]        # same media, in the same order
    assert all(f[2] != s[2] for f, s in zip(first, second, strict=True))           # but never the same move
    assert all(a[2] != b[2] for a, b in itertools.pairwise(first))                 # and neighbours differ too
    assert [c[1] for c in first] == [0] * 4 and [c[1] for c in second] == [1] * 4  # cycle count drives the stock-clip offset


def test_short_media_pool_starts_with_its_own_section_then_borrows_from_the_nearest_neighbours():
    from autopilot.shots import short_media_pool

    sections = [[{"id": f"s{i}m{k}"} for k in range(3)] for i in range(6)]
    pool = short_media_pool(sections, 2, want=8)
    ids = [m["id"] for m in pool]
    assert ids[:3] == ["s2m0", "s2m1", "s2m2"]                      # its own first
    assert {"s1m0", "s3m0"} <= set(ids[3:]) and len(pool) >= 8     # then the adjacent sections
    assert short_media_pool([[], [], []], 1) == []                  # nothing anywhere: empty, the card fallback handles it


def test_shorts_repeat_a_picture_at_most_once_and_cut_slower_when_media_is_scarce():
    from autopilot.shots import SHORT_CUT_SECONDS, SHORT_MAX_REUSE, plan_cuts

    plan = plan_cuts(_sections(50.0), [12], 24, SHORT_CUT_SECONDS, SHORT_MAX_REUSE)
    assert len(plan[0]) == round(50 / SHORT_CUT_SECONDS)            # 12 items x 2 allows 24 cuts: no cap hit
    assert len(plan_cuts(_sections(50.0), [6], 24, SHORT_CUT_SECONDS, SHORT_MAX_REUSE)[0]) == 12   # 6 items: slower cuts, not more repeats


def test_best_first_ranks_by_score_and_prefers_earlier_candidates_on_ties():
    from autopilot.shots import MIN_SCORE, best_first

    assert best_first([5, 9, 7, 9]) == [1, 3, 2, 0]
    assert best_first([MIN_SCORE] * 5) == [0, 1, 2, 3, 4]      # rating unavailable: keep the most specific results, in order
    assert best_first([]) == []


def test_a_reused_image_shows_a_different_part_each_time():
    from autopilot.render import _motion

    first, second, third = _motion(0, 100, 0), _motion(0, 100, 1), _motion(0, 100, 2)
    assert len({first, second, third}) == 3                       # three different camera moves for the same picture
    assert second[0] == third[0] == "1.4" and "0.12" in second[2] and "0.88" in third[2]   # top band, then bottom band
    assert "on/100" in second[1] and "1-on/100" in third[1]       # panning in opposite directions


def test_sparse_sections_borrow_from_their_nearest_neighbours_and_mark_the_loans():
    from autopilot.shots import fill_sparse_sections

    sections = [[{"id": "a0"}, {"id": "a1"}], [{"id": f"b{k}"} for k in range(6)], [{"id": "c0"}], [{"id": f"d{k}"} for k in range(5)]]
    out = fill_sparse_sections(sections, min_items=5)
    assert out[1] == sections[1] and out[3] == sections[3]                      # well-supplied sections are untouched
    assert [m["id"] for m in out[0][:2]] == ["a0", "a1"] and len(out[0]) >= 5   # keeps its own first, then borrows
    assert all(m.get("borrowed") for m in out[0][2:]) and not any(m.get("borrowed") for m in out[0][:2])
    assert out[0][2]["id"].startswith("b")                                      # from the nearest section
    assert len(out[2]) >= 5 and out[2][0] == {"id": "c0"}
    assert fill_sparse_sections([[], []], min_items=5) == [[], []]              # nothing anywhere: stays empty (title cards)


def test_sibling_shorts_get_different_pictures_even_when_the_video_has_little_media():
    from autopilot.shots import distinct_short_pool

    sections = [[{"kind": "image", "path": f"s{i}_{n}"} for n in range(2)] for i in range(6)]          # 12 pictures for 6 sections
    pools = [distinct_short_pool(sections, [0, 2, 4], k) for k in range(3)]
    firsts = [{m["path"] for m in p[:4]} for p in pools]
    assert firsts[0].isdisjoint(firsts[1]) and firsts[1].isdisjoint(firsts[2]) and firsts[0].isdisjoint(firsts[2])
    assert all(p[0]["path"].startswith(f"s{[0, 2, 4][k]}_") for k, p in enumerate(pools))                # each starts in its own section
    assert all(len({m["path"] for m in p}) == len(p) and 6 <= len(p) <= 12 for p in pools)              # no duplicates, enough to cut
    rich = [[{"kind": "image", "path": f"r{i}_{n}"} for n in range(6)] for i in range(6)]              # lots of media: bigger shares
    big = [distinct_short_pool(rich, [0, 2, 4], k) for k in range(3)]
    assert all(len(p) >= 9 for p in big) and not ({m["path"] for m in big[0][:6]} & {m["path"] for m in big[1][:6]})
    assert distinct_short_pool([[], [], []], [0, 1, 2], 1) == []


def test_pixabay_photos_are_offered_as_extra_still_pictures(monkeypatch):
    from autopilot import stock

    monkeypatch.setattr(stock, "search_photos", lambda q, limit=8, min_width=1600: [{"kind": "photo", "id": 7, "url": "u", "thumb": "t", "title": "battery", "page": "p", "artist": "a"}])
    got = stock.search_picture_candidates("battery")
    assert got[0]["kind"] == "image" and got[0]["source"] == "pixabay_photo"
    assert "Pixabay" in stock.credit_line_photo(got[0])
