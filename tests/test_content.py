from autopilot.qa import check_script, deterministic_checks
from autopilot.script import generate_script

SOURCE = {"title": "Laser", "url": "https://en.wikipedia.org/wiki/Laser", "text": "A laser emits light."}


def _script(words=700, **over):
    s = {"title": "How lasers work", "claims": ["A laser emits light."],
         "sections": [{"heading": "h", "narration": "word " * words, "visual_query": "laser beam"}]}
    s.update(over)
    return s


def _punchy(n, word="Word"):
    """About n words in short sentences, so the punch-up pass has nothing to fix."""
    return (f"{word} {word.lower()} {word.lower()} end. " * (n // 4 + 1)).strip()


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
        return {"narration": _punchy(n), "claims": [f"claim{calls['sections']}"]}

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
        {"heading": "A", "narration": _punchy(200, "Keep"), "claims": ["c0"], "key_points": ["k"]},
        {"heading": "B", "narration": _punchy(200, "Old"), "claims": ["bad"], "key_points": ["k"]}]}
    prompts = []

    def gen(prompt):
        prompts.append(prompt)
        return {"narration": _punchy(200, "New"), "claims": ["good"]}

    out = repair_sections(script, SOURCE, [1], ["the bad claim"], gen=gen)
    assert len(prompts) == 1 and "the bad claim" in prompts[0] and "UNSUPPORTED" in prompts[0]
    assert out["sections"][0]["narration"].startswith("Keep") and out["sections"][1]["narration"].startswith("New")
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



# ---------- punchy style ----------
LONG_WINDED = ("When you consider the fundamental physical principles that govern the behaviour of light inside a resonant "
               "optical cavity, it becomes apparent that the amplification of coherent radiation depends upon a delicate "
               "balance between the stimulated emission of photons and the various loss mechanisms present. ") * 3
SNAPPY = "Light bounces. It grows. You get a beam. That is a laser. "


def test_style_stats_measure_sentence_length_hook_and_direct_address():
    from autopilot.script import style_stats

    s = style_stats("Ever seen a laser cut steel? You can. It is wild. Your eyes can't track it.")
    assert s["sentences"] == 4 and s["hook"] == 6 and s["longest"] == 6 and s["long_share"] == 0
    assert s["you_per_1000"] > 100 and style_stats(LONG_WINDED)["avg"] > 30


def test_needs_punch_flags_long_winded_text_and_long_hooks_but_not_snappy_text():
    from autopilot.script import needs_punch

    assert needs_punch(LONG_WINDED, first=False) and not needs_punch(SNAPPY * 10, first=False)
    long_hook = "This is a very long opening sentence that rambles on for well over sixteen words before it finally stops. Short. Ok. Yes."
    assert needs_punch(long_hook, first=True) and not needs_punch(long_hook, first=False)  # the hook limit applies to section 1 only


def test_section_prompt_carries_the_voice_rules_and_the_hook_rule_only_for_the_first_section():
    from autopilot.script import _write_section
    script = {"title": "T", "sections": [{"heading": "A", "key_points": ["k"], "visual_query": "q", "narration": ""},
                                          {"heading": "B", "key_points": ["k"], "visual_query": "q", "narration": ""}]}
    prompts = []
    for i in (0, 1):
        _write_section(script, i, SOURCE, "", 120, lambda p: prompts.append(p) or {"narration": _punchy(130), "claims": []})
    assert "every four" in prompts[0] and "ONE viewer" in prompts[0] and "Short, punchy sentences" in prompts[0]
    assert "AT MOST 12 words" in prompts[0] and "AT MOST 12 words" not in prompts[1]


def test_long_winded_section_gets_one_punch_up_pass_and_the_better_version_is_kept():
    from autopilot.script import _write_section

    script = {"title": "T", "sections": [{"heading": "A", "key_points": ["k"], "visual_query": "q", "narration": ""}]}
    prompts = []

    def gen(prompt):
        prompts.append(prompt)
        if "Rewrite this narration" in prompt:
            return {"narration": SNAPPY * 20, "claims": ["rewritten claim"]}
        return {"narration": LONG_WINDED, "claims": ["original claim"]}

    out = _write_section(script, 0, SOURCE, "", 100, gen)
    assert sum("Rewrite this narration" in p for p in prompts) == 1
    assert out["narration"].startswith("Light bounces") and out["claims"] == ["rewritten claim"]  # claims follow the new text
    assert "SOURCE (Laser) for checking facts" in prompts[-1]


def test_punch_up_is_skipped_when_text_is_already_punchy_and_ignored_when_it_makes_things_worse():
    from autopilot.script import _write_section

    script = {"title": "T", "sections": [{"heading": "A", "key_points": ["k"], "visual_query": "q", "narration": ""}]}
    calls = []
    out = _write_section(script, 0, SOURCE, "", 100, lambda p: calls.append(p) or {"narration": SNAPPY * 20, "claims": ["c"]})
    assert len(calls) == 1 and out["claims"] == ["c"]                                  # nothing to fix: no extra call

    def worse(prompt):
        return {"narration": LONG_WINDED * 2 if "Rewrite this narration" in prompt else LONG_WINDED, "claims": ["c"]}

    kept = _write_section(script, 0, SOURCE, "", 100, worse)
    assert kept["narration"] == LONG_WINDED.strip()                                    # the rewrite was not better: keep the draft


def test_comparison_check_reads_the_narration_not_the_writers_claim_list():
    from autopilot import qa

    script = {"sections": [{"narration": "Jupiter is big. The average density is 1.326 g/cm3. It is lighter than water, yet massive. Its mass is 318 times Earth's."}]}
    assert qa.comparison_sentences(script) == ["It is lighter than water, yet massive.", "Its mass is 318 times Earth's."]
    prompts = []

    def gen(prompt):
        prompts.append(prompt)
        return {"wrong": [{"n": 1, "why": "1.326 g/cm3 is denser than water"}, {"n": 9, "why": "bad index"}, {"n": "x"}]}

    issues = qa.comparison_issues(script, {"text": "SOURCE TEXT"}, gen)
    assert issues == ["unsupported claim: It is lighter than water, yet massive."]            # a bad index from the model is ignored
    assert "1. It is lighter than water" in prompts[0] and "SOURCE TEXT" in prompts[0] and "1 g/cm3" in prompts[0]
    assert qa.comparison_issues({"sections": [{"narration": "Nothing to compare here."}]}, {"text": "s"}, gen) == []


def test_comparison_check_retries_once_and_never_blocks_the_video(capsys):
    from autopilot import llm, qa

    calls = []

    def flaky(prompt):
        calls.append(1)
        if len(calls) == 1:
            raise llm.LLMUnavailable("busy")
        return {"wrong": [{"n": 1, "why": "wrong"}]}

    script = {"sections": [{"narration": "It is heavier than lead."}]}
    assert qa.comparison_issues(script, {"text": "s"}, flaky) == ["unsupported claim: It is heavier than lead."] and len(calls) == 2

    def down(prompt):
        raise llm.LLMUnavailable("quota")

    assert qa.comparison_issues(script, {"text": "s"}, down) == []
    assert "comparison check unavailable" in capsys.readouterr().out
