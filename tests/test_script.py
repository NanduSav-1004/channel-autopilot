

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
