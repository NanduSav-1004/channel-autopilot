from autopilot.qa import check_script, deterministic_checks
from autopilot.script import generate_script

SOURCE = {"title": "Laser", "url": "https://en.wikipedia.org/wiki/Laser", "text": "A laser emits light."}


def _script(words=700, **over):
    s = {"title": "How lasers work", "claims": ["A laser emits light."],
         "sections": [{"heading": "h", "narration": "word " * words, "visual_query": "laser beam"}]}
    s.update(over)
    return s


def _fake_llm(words_per_call=None, short_first=False):
    """Outline for 3 planned sections; each section call returns `words_per_call` words."""
    calls = {"prompts": [], "sections": 0}

    def gen(prompt):
        calls["prompts"].append(prompt)
        if "Plan exactly" in prompt:
            return {"title": "T", "thumbnail_text": "x", "description": "d", "tags": ["a"],
                    "sections": [{"heading": f"H{i}", "key_points": ["p"], "visual_query": f"q{i}"} for i in range(3)]}
        calls["sections"] += 1
        n = words_per_call
        if short_first and prompt.count("Your last draft") == 0 and calls["sections"] % 2 == 1:
            n = 5  # undershoot on the first try of every section
        return {"narration": ("word " * n).strip() + " end.", "claims": [f"claim{calls['sections']}"]}

    return gen, calls


def test_generate_script_assembles_sections_and_tags_series_and_source():
    gen, _calls = _fake_llm(words_per_call=500)
    out = generate_script("lasers", SOURCE, "science", series="how_it_works", words=1500, gen=gen)
    assert out["series"] == "how_it_works" and out["source_url"] == SOURCE["url"]
    assert [s["heading"] for s in out["sections"]] == ["H0", "H1", "H2"]
    assert [s["visual_query"] for s in out["sections"]] == ["q0", "q1", "q2"]
    assert out["claims"] == ["claim1", "claim2", "claim3"]
    assert sum(len(s["narration"].split()) for s in out["sections"]) >= 1500


def test_outline_prompt_contains_source_and_style():
    gen, calls = _fake_llm(words_per_call=500)
    generate_script("lasers", SOURCE, "science", series="what_if", gen=gen)
    assert "A laser emits light." in calls["prompts"][0] and "what if" in calls["prompts"][0].lower()


def test_short_section_is_retried_once_with_a_word_target():
    gen, calls = _fake_llm(words_per_call=500, short_first=True)
    generate_script("lasers", SOURCE, "science", gen=gen, words=1500)
    retried = [p for p in calls["prompts"] if "Your last draft" in p]
    assert retried and "at least 500" in retried[0]


def test_later_sections_get_continuity_from_previous_ending():
    gen, calls = _fake_llm(words_per_call=500)
    generate_script("lasers", SOURCE, "science", gen=gen)
    sec_prompts = [p for p in calls["prompts"] if "Write section" in p]
    assert "opening of the video" in sec_prompts[0] and "previous section ended with" in sec_prompts[1]
    assert "payoff" in sec_prompts[2]


def test_qa_feedback_goes_into_the_outline_prompt():
    gen, calls = _fake_llm(words_per_call=500)
    generate_script("lasers", SOURCE, "science", gen=gen, feedback=["too short"])
    assert "too short" in calls["prompts"][0]


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


def test_locate_sections_matches_paraphrased_claims_and_ignores_unrelated():
    from autopilot.qa import locate_sections
    s = {"sections": [{"claims": ["lasers emit coherent light"], "narration": "x"},
                      {"claims": ["the concept drives research into energy limits"], "narration": "y"}]}
    assert locate_sections(s, ["Even if never built, the concept drives research into energy limits"]) == [1]
    assert locate_sections(s, ["bananas are yellow fruit"]) == []


def test_repair_rewrites_only_target_sections_and_forwards_avoid_claims():
    from autopilot.script import repair_sections
    script = {"title": "T", "series": "what_if", "sections": [
        {"heading": "A", "narration": "keep " * 200, "claims": ["c0"], "key_points": ["k"]},
        {"heading": "B", "narration": "old " * 200, "claims": ["bad"], "key_points": ["k"]}]}
    prompts = []

    def gen(prompt):
        prompts.append(prompt)
        return {"narration": "new " * 200, "claims": ["good"]}

    out = repair_sections(script, SOURCE, [1], ["the bad claim"], gen=gen)
    assert len(prompts) == 1 and "the bad claim" in prompts[0] and "UNSUPPORTED" in prompts[0]
    assert out["sections"][0]["narration"].startswith("keep") and out["sections"][1]["narration"].startswith("new")
    assert out["claims"] == ["c0", "good"]


def test_metadata_claims_tag_title_and_description_sentences():
    from autopilot.qa import metadata_claims
    s = {"title": "T title", "description": "Short. This sentence has enough words to count. Another long enough sentence here."}
    claims = metadata_claims(s)
    assert claims[0] == "[title] T title" and len(claims) == 3 and all(c.startswith(("[title]", "[description]")) for c in claims)


def test_check_script_sends_metadata_to_the_fact_checker():
    seen = {}

    def gen(prompt):
        seen["p"] = prompt
        return {"unsupported": ["[description] Lasers were invented in 1850 by someone."], "advice_given": False}

    s = _script(description="Lasers were invented in 1850 by someone.")
    issues = check_script(s, SOURCE, [], gen=gen)
    assert "[description] Lasers were invented" in seen["p"]
    assert issues == ["unsupported claim: [description] Lasers were invented in 1850 by someone."]


def test_repair_metadata_rewrites_title_and_description_only():
    from autopilot.script import repair_metadata
    s = {"title": "Old", "description": "Old desc", "sections": [{"narration": "keep"}]}
    out = repair_metadata(s, SOURCE, ["[description] bad"], gen=lambda p: {"title": " New ", "description": "New desc"})
    assert out["title"] == "New" and out["description"] == "New desc" and out["sections"] == [{"narration": "keep"}]


def test_relevant_excerpt_keeps_the_lead_and_best_matching_paragraphs_in_order_within_budget():
    from autopilot.script import relevant_excerpt

    paras = [f"Lead paragraph {i} about the general topic." for i in range(2)]
    paras += [f"Filler paragraph number {i} about unrelated things entirely." * 3 for i in range(30)]
    paras.insert(20, "Stimulated emission occurs when a photon triggers excited atoms to emit coherent photons.")
    text = "\n".join(paras)
    out = relevant_excerpt(text, "stimulated emission coherent photons", max_chars=700)
    assert out.startswith("Lead paragraph 0") and "Stimulated emission occurs" in out
    assert len(out) <= 700 + len(paras[0]) and out.index("Lead paragraph 1") < out.index("Stimulated emission")


def test_short_sources_are_sent_whole():
    from autopilot.script import relevant_excerpt
    assert relevant_excerpt("short text", "anything") == "short text"


def test_section_prompt_uses_the_excerpt_not_the_whole_article():
    big = "\n".join(f"Paragraph {i} " + "word " * 60 for i in range(200))  # ~60,000 chars
    seen = []
    script = {"title": "T", "sections": [{"heading": "H", "key_points": ["paragraph 7"], "visual_query": "q", "narration": ""}]}
    from autopilot.script import _write_section
    _write_section(script, 0, {"title": "S", "text": big}, "", 200, lambda p: seen.append(p) or {"narration": "w " * 200, "claims": []})
    assert len(seen[0]) < 12000 and "Paragraph 0" in seen[0]


def test_factcheck_prompt_ignores_framing_and_paraphrase_but_flags_specifics():
    from autopilot.qa import FACTCHECK_PROMPT
    assert "rhetorical questions" in FACTCHECK_PROMPT and "paraphrase" in FACTCHECK_PROMPT
    assert "number, date, name" in FACTCHECK_PROMPT
