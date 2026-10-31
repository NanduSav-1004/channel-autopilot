

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
