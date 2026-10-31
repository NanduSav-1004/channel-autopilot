from autopilot import closing, render
from autopilot.config import Config, cta_on


def _script():
    return {"title": "How Lasers Work", "sections": [{"heading": "a", "narration": "First."}, {"heading": "z", "narration": "And that is how a laser works."}]}


def test_closing_line_is_added_once_to_the_last_section():
    out = closing.add_closing(_script(), 3, gen=lambda p: {"closing": "Curious what we will take apart tomorrow? Subscribe for a new science explainer every day."})
    assert out["sections"][-1]["narration"].endswith("every day.") and out["sections"][0]["narration"] == "First."
    again = closing.add_closing(out, 4, gen=lambda p: {"closing": "Subscribe, subscribe, subscribe for more explainers like this one."})
    assert again["closing"] == out["closing"] and again["sections"][-1]["narration"] == out["sections"][-1]["narration"]   # unchanged the second time


def test_a_bad_model_answer_falls_back_to_a_clean_template():
    for bad in ({"closing": "Like and subscribe, smash that bell!"}, {"closing": "Subscribe for 3 more."}, {"closing": "Thanks."}, {},
                {"closing": "Thanks for watching, hit that subscribe button and join us on the journey!"},
                {"closing": "If you enjoyed this one, subscribe and we will explore more wonders together."}):
        out = closing.add_closing(_script(), 2, gen=lambda p, b=bad: b)
        line = out["closing"]
        assert closing.valid(line) and line == closing.FALLBACKS[2 % len(closing.FALLBACKS)]


def test_a_failing_model_never_stops_the_video():
    def boom(prompt):
        raise closing.llm.LLMUnavailable("quota")

    assert closing.valid(closing.add_closing(_script(), 0, gen=boom)["closing"])


def test_styles_rotate_with_the_job_so_neighbours_differ():
    seen = {closing.make_closing("T", "x", n, gen=lambda p: {}) for n in range(len(closing.FALLBACKS))}
    assert len(seen) == len(closing.FALLBACKS)


def test_cta_flags_default_off():
    assert not cta_on(Config(niche="n", audience="a", formats={}), "long_closing")
    assert cta_on(Config(niche="n", audience="a", formats={}, cta={"short_tag": True}), "short_tag")


def test_short_tag_is_added_to_the_caption_file(tmp_path):
    ass = tmp_path / "c.ass"
    ass.write_text("[V4+ Styles]\nFormat: Name\nStyle: Cap,Lato\n\n[Events]\nFormat: Layer\nDialogue: 0,0:00:00.00,0:00:01.00,Cap,Hi\n", encoding="utf-8")
    render.add_cta_tag(ass, "FULL VIDEO ON THE CHANNEL", 26.0, 28.7, "Lato")
    text = ass.read_text(encoding="utf-8")
    assert "Style: Cta,Lato" in text and "Dialogue: 1,0:00:26.00,0:00:28.70,Cta," in text and "FULL VIDEO ON THE CHANNEL" in text
    assert text.index("Style: Cta") < text.index("[Events]")
