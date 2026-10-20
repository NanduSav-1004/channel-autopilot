from PIL import Image

from autopilot import llm
from autopilot.shots import MIN_SCORE, plan_queries, rate_candidates

SCRIPT = {"title": "T", "sections": [
    {"heading": "A", "narration": "alpha " * 50, "visual_query": "alpha thing"},
    {"heading": "B", "narration": "beta " * 50, "visual_query": "beta thing"},
]}


def test_plan_queries_puts_llm_queries_first_and_keeps_fallbacks():
    out = plan_queries(SCRIPT, "topic", gen=lambda p: {"sections": [{"queries": ["q1"], "stock": ["s1"]}, {"queries": ["q2"]}]})
    assert out[0]["commons"][0] == "q1" and "alpha thing" in out[0]["commons"]
    assert out[0]["stock"][0] == "s1" and out[1]["commons"][0] == "q2" and out[1]["stock"]


def test_plan_queries_falls_back_on_llm_error_or_wrong_count():
    def boom(p):
        raise llm.LLMError("x")

    assert plan_queries(SCRIPT, "topic", gen=boom)[0]["commons"][0] == "alpha thing"
    assert plan_queries(SCRIPT, "topic", gen=lambda p: {"sections": [{"queries": ["only one"]}]})[0]["commons"][0] == "alpha thing"


def test_rate_candidates_returns_scores_and_neutral_on_failure(tmp_path):
    p = tmp_path / "a.jpg"
    Image.new("RGB", (64, 64)).save(p)
    assert rate_candidates(SCRIPT["sections"][0], [p], ["t"], gen=lambda prompt, images: {"scores": [9]}) == [9]
    assert rate_candidates(SCRIPT["sections"][0], [p], ["t"], gen=lambda prompt, images: {"scores": [1, 2]}) == [MIN_SCORE]


def test_interleave_alternates_kinds():
    from autopilot.shots import _interleave
    items = [{"kind": "image", "n": 1}, {"kind": "image", "n": 2}, {"kind": "video", "n": 3}]
    assert [i["n"] for i in _interleave(items)] == [1, 3, 2]


def test_stock_parse_hits_skips_low_quality_ai_and_small():
    from autopilot.stock import parse_hits
    base = {"id": 1, "tags": "t", "duration": 10, "pageURL": "p", "user": "u",
            "videos": {"medium": {"url": "v", "width": 1280, "thumbnail": "th"}}}
    data = {"hits": [base, {**base, "isLowQuality": True}, {**base, "isAiGenerated": True},
                     {**base, "duration": 2}, {**base, "videos": {"medium": {"url": "v", "width": 640, "thumbnail": "x"}}}]}
    assert len(parse_hits(data)) == 1
