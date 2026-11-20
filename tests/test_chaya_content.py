import importlib
import json
from pathlib import Path

from autopilot import malayalam

ROOT = Path(__file__).resolve().parents[1]


def test_every_queued_video_exists_and_each_beat_is_one_sentence():
    queue = json.loads((ROOT / "chaya" / "queue.json").read_text())
    ids = [q["id"] for q in queue]
    assert len(ids) == len(set(ids))
    for q in queue:
        mod = importlib.import_module(f"chaya.content_{q['content']}")
        video = next(v for v in mod.VIDEOS if v["id"] == q["id"])
        assert mod.FACTS and video["title_ml"] and video["thumb"]["ml"]
        assert video["beats"][0]["scene"], "the first beat needs a scene"
        for b in video["beats"]:
            assert len(malayalam.split_sentences_ml(b["t"])) == 1, f"{q['id']}: {b['t'][:40]}"
        if video["orient"] == "tall":
            assert "#Shorts" in video["title_ml"]
