from autopilot.qa import check_script, deterministic_checks
from autopilot.script import generate_script

SOURCE = {"title": "Laser", "url": "https://en.wikipedia.org/wiki/Laser", "text": "A laser emits light."}


def _script(words=700, **over):
    s = {"title": "How lasers work", "claims": ["A laser emits light."],
         "sections": [{"heading": "h", "narration": "word " * words, "visual_query": "laser beam"}]}
    s.update(over)
    return s


def test_generate_script_tags_series_and_source():
    out = generate_script("lasers", SOURCE, "science", series="how_it_works", gen=lambda p: {"title": "t"})
    assert out["series"] == "how_it_works" and out["source_url"] == SOURCE["url"]


def test_prompt_contains_source_and_style():
    seen = {}
    generate_script("lasers", SOURCE, "science", series="what_if", gen=lambda p: seen.setdefault("p", p) and {})
    assert "A laser emits light." in seen["p"] and "what if" in seen["p"].lower()


def test_too_short_script_rejected():
    assert any("too short" in i for i in deterministic_checks(_script(words=10), []))


def test_forbidden_topic_rejected():
    s = _script()
    s["sections"][0]["narration"] += " this is financial advice"
    assert any("forbidden" in i for i in deterministic_checks(s, ["financial advice"]))


def test_unsupported_claim_and_advice_flagged():
    verdict = {"unsupported": ["Lasers were invented in 1850"], "advice_given": True}
    issues = check_script(_script(), SOURCE, [], gen=lambda p: verdict)
    assert any("1850" in i for i in issues) and any("advice" in i for i in issues)


def test_clean_script_passes():
    assert check_script(_script(), SOURCE, [], gen=lambda p: {"unsupported": [], "advice_given": False}) == []


def test_too_few_sections_rejected():
    s = _script(words=2000)  # one long section
    assert any("too few sections" in i for i in deterministic_checks(s, [], min_words=100, min_sections=6))
