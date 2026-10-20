from PIL import Image

from autopilot.metadata import build_description, chapter_marks, clean_tags, clean_title
from autopilot.thumbnail import make_thumbnail, thumbnail_text


def test_description_has_credits_disclosure_and_respects_limit():
    d = build_description({"description": "About lasers."}, ["credit " * 10] * 1000, "https://x")
    assert "About lasers." in d and "synthetic voice" in d and len(d) <= 5000


def test_chapters_format_and_minimum():
    t = [{"start": 0, "heading": "A"}, {"start": 89, "heading": "B"}, {"start": 176, "heading": "C"}]
    assert chapter_marks(t) == [("0:00", "A"), ("1:29", "B"), ("2:56", "C")]
    assert chapter_marks(t[:2]) == []


def test_tags_deduped_and_length_capped():
    tags = clean_tags(["MRI", "mri", "<b>x</b>"] + [f"tag{i}" * 5 for i in range(200)])
    assert tags.count("MRI") == 1 and sum(len(t) + 1 for t in tags) <= 450


def test_title_limited_to_100_chars():
    assert len(clean_title("x" * 300)) == 100


def test_thumbnail_text_limits_words():
    assert thumbnail_text({"title": "a b c d e f g: rest"}) == "A B C D E"


def test_make_thumbnail_without_and_with_background(tmp_path):
    s = {"title": "How MRI Works: From Spin to Image"}
    out = make_thumbnail(s, None, tmp_path / "t.jpg")
    assert Image.open(out).size == (1280, 720)
    bg = tmp_path / "bg.jpg"
    Image.new("RGB", (2000, 900), (200, 50, 50)).save(bg)
    out2 = make_thumbnail(s, bg, tmp_path / "t2.jpg")
    assert Image.open(out2).size == (1280, 720) and out2.stat().st_size < 2_000_000
