"""usage: python chaya/enqueue.py <content suffix> -- appends its videos to chaya/queue.json, Shorts first, the long video third."""
import importlib, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
name = sys.argv[1]
mod = importlib.import_module(f"chaya.content_{name}")
q = json.loads((ROOT / "chaya" / "queue.json").read_text())
have = {e["id"] for e in q}
vids = [v for v in mod.VIDEOS if v["id"] not in have]
long_ = [v for v in vids if v["orient"] == "wide"]
shorts = [v for v in vids if v["orient"] == "tall"]
order = shorts[:2] + long_ + shorts[2:]
q += [{"content": name, "id": v["id"]} for v in order]
(ROOT / "chaya" / "queue.json").write_text(json.dumps(q, ensure_ascii=False, indent=1))
print(len(q), [v["id"] for v in order])
