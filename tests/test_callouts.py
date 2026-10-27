from autopilot.callouts import callout_for, find_callouts


def _w(text, s=0.0):
    return {"w": text, "s": s, "e": s + 0.3}


def _words(text, t0=0.0):
    return [_w(w, t0 + i * 0.4) for i, w in enumerate(text.split())]


def test_a_figure_with_its_units_is_shown_and_a_bare_small_number_is_not():
    ws = _words("They sent 319 terabits per second over 3000 km using four cores")
    assert callout_for(ws, 2) == "319 terabits per second"
    assert callout_for(ws, 7) == "3000 km"
    assert callout_for(_words("There were 7 steps"), 2) is None


def test_years_and_temperatures_are_shown():
    assert callout_for(_words("In 1911 Kamerlingh"), 1) == "1911"
    assert callout_for(_words("cooled to 4.2 kelvin."), 2) == "4.2 kelvin"
    assert callout_for(_words("at –238 °C, a"), 1) == "–238 °C"
    assert callout_for(_words("a 35K record"), 1) is None or callout_for(_words("a 35K record"), 1).startswith("35")
    assert callout_for(_words("about 12345 things"), 1) is None             # a bare big number is not a year


def test_callouts_are_spaced_out_and_timed_from_the_spoken_word():
    s1 = {"text": "x", "start": 0.0, "end": 6.0, "words": _words("In 1911 it cooled to 4.2 kelvin.")}
    s2 = {"text": "x", "start": 20.0, "end": 24.0, "words": _words("Then in 1933 Meissner found", 20.0)}
    out = find_callouts([{"sentences": [s1, s2]}], min_gap=7.0)
    assert [c["text"] for c in out] == ["1911", "1933"]              # "4.2 kelvin" came 1.6 s after: too close
    assert abs(out[0]["start"] - (0.4 - 0.05)) < 1e-6 and out[0]["end"] - out[0]["start"] == 2.8


def test_malayalam_sentences_without_digits_give_no_callouts():
    assert find_callouts([{"sentences": [{"text": "x", "start": 0, "end": 3, "words": _words("ഒന്ന് രണ്ട് മൂന്ന്")}]}]) == []
