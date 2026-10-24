

def test_key_word_prefers_a_substantial_last_word():
    from autopilot.thumbnail import key_word

    assert key_word("HOTTER FREEZES FASTER?") == "FASTER?"
    assert key_word("FASTER THAN IT") == "FASTER"


def test_fit_makes_headline_big_and_inside_the_box():
    from PIL import Image, ImageDraw

    from autopilot.thumbnail import _fit

    draw = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    lines, size = _fit("ZERO RESISTANCE MYTH", draw, 820, 500)
    assert " ".join(lines) == "ZERO RESISTANCE MYTH" and size >= 100


def test_vision_pick_uses_the_models_choice_and_falls_back_on_failure(tmp_path):
    from PIL import Image

    from autopilot import llm
    from autopilot.thumbnail import pick_with_vision

    paths = []
    for i, c in enumerate(((250, 20, 20), (20, 20, 250), (20, 250, 20))):
        p = tmp_path / f"{i}.jpg"
        Image.effect_noise((1200, 700), 60).convert("RGB").point(lambda v, c=c: v).save(p)
        paths.append(p)
    script = {"title": "T"}
    chosen = pick_with_vision(script, paths, gen=lambda *a, **k: {"best": 2})
    assert chosen in paths

    def boom(*a, **k):
        raise llm.LLMError("down")

    assert pick_with_vision(script, paths, gen=boom) in paths


def test_make_thumbnail_is_1280x720_without_any_image(tmp_path):
    from PIL import Image

    from autopilot.thumbnail import make_thumbnail

    out = make_thumbnail({"title": "A: b", "thumbnail_text": "Why ice floats", "series": "how_it_works"}, [], tmp_path / "t.jpg")
    assert Image.open(out).size == (1280, 720)
