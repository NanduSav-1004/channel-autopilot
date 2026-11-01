

def test_shorten_title_uses_the_model_then_falls_back_to_trimming():
    from autopilot import llm
    from autopilot.script import TITLE_MAX, shorten_title, trim_title

    long = "The Mpemba Effect: Why Hot Water Can Sometimes Freeze Faster Than Cold Water Under Odd Conditions"
    assert len(long) > TITLE_MAX
    s = {"title": long}
    assert shorten_title(s, gen=lambda p: {"title": "Why Hot Water Can Freeze Faster"}) and s["title"] == "Why Hot Water Can Freeze Faster"
    s = {"title": long}
    assert shorten_title(s, gen=lambda p: {"title": long}) and len(s["title"]) <= TITLE_MAX   # model ignored the limit

    def boom(p):
        raise llm.LLMError("down")

    s = {"title": long}
    shorten_title(s, gen=boom)
    assert s["title"] == "The Mpemba Effect"
    s = {"title": "Short title"}
    assert not shorten_title(s, gen=boom) and s["title"] == "Short title"
    assert len(trim_title("word " * 30)) <= TITLE_MAX


def test_strip_recap_cuts_opening_recaps_but_keeps_real_content():
    from autopilot.script import strip_recap

    body = "Jupiter has a core. It is hot. It is dense. Pressure crushes it."
    assert strip_recap("You just heard how big it is. " + body) == body
    assert strip_recap("You've seen the size. Now that you know the mass, look inside. " + body) == body
    assert strip_recap(body) == body                                          # nothing to cut
    short = "You just heard that. Okay."
    assert strip_recap(short) == short                                        # never cut a section down to almost nothing


def test_the_opening_may_not_be_a_numbers_dump():
    from autopilot.script import cold_open_ok, opening_numbers

    dump = "Jupiter is 142,976 km wide. It weighs 318 times Earth. Its volume is 1,321 Earths. Its day is 10 hours."
    calm = "What if Jupiter hit us? The answer is brutal, and you will see why. Picture a marble hitting a grape. It is 11 times wider."
    assert opening_numbers(dump) == 4 and not cold_open_ok(dump)
    assert cold_open_ok(calm)


def test_cold_open_is_rewritten_once_when_it_is_a_numbers_dump():
    from autopilot.script import _write_section

    dump = ("What if Jupiter hit us? Jupiter is 142,976 km wide. It weighs 318 times Earth. Its volume is 1,321 Earths. " + "Filler sentence here. " * 30)
    calm = ("What if Jupiter hit us? You would not survive, and you will see exactly why. " + "Picture a marble and a grape. " * 30).strip()
    calls = []

    def gen(prompt):
        calls.append(prompt)
        return {"narration": calm if "COLD OPEN" in prompt and "Rewrite the OPENING" in prompt else dump, "claims": []}

    script = {"title": "T", "sections": [{"heading": "a", "key_points": []}, {"heading": "b", "key_points": []}]}
    out = _write_section(script, 0, {"title": "S", "text": "x"}, "style", 20, gen)
    assert out["narration"] == calm and any("Rewrite the OPENING" in c for c in calls)


def test_title_must_keep_the_topics_words_or_is_rewritten():
    from autopilot.script import fit_title, title_fits_topic

    topic = "What if Jupiter collided with Earth?"
    assert not title_fits_topic("Jupiter's Size and Mass Compared to Earth", topic)
    assert title_fits_topic("What if Jupiter collided with Earth?", topic) and title_fits_topic("Jupiter Collides With Earth: What Then?", topic)
    script = {"title": "Jupiter's Size and Mass Compared to Earth", "sections": [{"heading": "h", "narration": "One two three."}]}
    note = fit_title(script, topic, gen=lambda p: {"answers_topic": True, "title": "What if Jupiter Collided With Earth?"})
    assert script["title"] == "What if Jupiter Collided With Earth?" and "->" in note and "NOT" not in note
    script = {"title": "Jupiter's Size and Mass Compared to Earth", "sections": [{"heading": "h", "narration": "One two three."}]}
    note = fit_title(script, topic, gen=lambda p: {"answers_topic": False, "title": "How Big Jupiter Really Is"})
    assert "does NOT answer" in note and script["title"] == "How Big Jupiter Really Is"          # honest title, and the warning is logged
    keep = {"title": "What if Jupiter Collided With Earth?", "sections": []}
    assert fit_title(keep, topic, gen=lambda p: 1 / 0) is None                                   # nothing to do, the model is never asked


def test_a_section_far_over_its_budget_is_tightened_once():
    from autopilot.script import MAX_OVER, _write_section

    long = "Jupiter is huge. " * 60                      # 180 words against a budget of 100
    short = "Jupiter is huge. " * 40                      # 120 words
    prompts = []

    def gen(prompt):
        prompts.append(prompt)
        return {"narration": short if "Rewrite this narration shorter" in prompt else long, "claims": ["c"]}

    script = {"title": "T", "sections": [{"heading": "a", "key_points": []}, {"heading": "b", "key_points": []}]}
    out = _write_section(script, 1, {"title": "S", "text": "x"}, "style", 100, gen)
    assert len(out["narration"].split()) == 120 and sum("Rewrite this narration shorter" in p for p in prompts) == 1
    assert 180 > 100 * MAX_OVER                          # that draft really was over the limit
    near = _write_section(script, 1, {"title": "S", "text": "x"}, "style", 130, lambda p: {"narration": long, "claims": []})
    assert len(near["narration"].split()) == 180          # within 1.5x of its budget: left alone


def test_a_model_answer_that_is_a_list_does_not_crash_the_script():
    from autopilot.script import _d, _write_section

    assert _d({"a": 1}) == {"a": 1} and _d([{"narration": "x"}]) == {"narration": "x"} and _d([]) == {} and _d("text") == {} and _d(None) == {}
    script = {"title": "T", "sections": [{"heading": "a", "key_points": []}, {"heading": "b", "key_points": []}]}
    out = _write_section(script, 1, {"title": "S", "text": "x"}, "style", 20, lambda p: [{"narration": "One two three. " * 12, "claims": []}])
    assert out["narration"].startswith("One two three.")


def test_repaired_sections_keep_to_the_section_budget():
    from autopilot.script import repair_sections

    big = "word " * 400
    script = {"title": "T", "per": 150, "series": "", "sections": [{"heading": "a", "key_points": [], "narration": big, "claims": []}]}
    seen = []

    def gen(prompt):
        seen.append(prompt)
        return {"narration": "ok " * 100, "claims": []}

    repair_sections(script, {"title": "S", "text": "x"}, [0], ["bad"], gen)
    assert "AT LEAST 180 spoken words" in seen[0]                         # 1.2 x the budget of 150, not the 400 it had grown to
