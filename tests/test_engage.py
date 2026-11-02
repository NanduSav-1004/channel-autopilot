from autopilot import engage


def test_questions_rotate_through_the_four_kinds():
    assert [engage.pick_kind(i) for i in range(5)] == ["pick", "personal", "correct", "request", "pick"]


def test_a_clean_model_question_is_used_and_a_bad_one_falls_back():
    good = lambda p: {"question": "Which would you have guessed was bigger?", "onscreen": "Which would you guess?", "comment": "Which would you have guessed was bigger? Tell us below."}
    out = engage.make_question("T", "last words", 0, good)
    assert out["question"].startswith("Which would you") and out["onscreen"] == "WHICH WOULD YOU GUESS" and out["kind"] == "pick"
    assert out["comment"].startswith("Which would you have guessed")
    for bad in ("Comment YES if you agree!", "Is it 5 or 6?", "Win a prize: which is bigger?", "Tell us everything", "What? Why?"):
        got = engage.make_question("T", "x", 1, lambda p, b=bad: {"question": b, "onscreen": "x", "comment": "x"})
        assert got["question"] == engage.FALLBACK["personal"]
    boom = engage.make_question("T", "x", 2, lambda p: (_ for _ in ()).throw(ValueError("down")))
    assert boom["question"] == engage.FALLBACK["correct"]
    assert engage.make_question("T", "x", 3, lambda p: {}, data=True)["question"] == engage.FALLBACK_DATA["request"]


def test_the_spoken_closing_and_extracting_a_question_from_a_narration():
    line = engage.closing_line({"question": "Which surprised you?"}, 1)
    assert line == "Which surprised you? Tell us in the comments. A new one comes every day, so subscribe."
    assert engage.extract_question("The trend reversed. Where does your state rank? Subscribe for more.") == "Where does your state rank?"
    assert engage.extract_question("Nothing to ask here. Subscribe.") is None
    assert engage.extract_question("Is it 5 or 6? Where do you live?") == "Where do you live?"


def test_last_question_works_in_any_language():
    assert engage.last_question("ഒന്ന്. നമ്മൾ എന്തെങ്കിലും വിട്ടുപോയോ? കമന്റിൽ പറയൂ.") == "നമ്മൾ എന്തെങ്കിലും വിട്ടുപോയോ?"
    assert engage.last_question("No question here.") is None and engage.last_question("Why? Because. And you, is it really so?") == "And you, is it really so?"
