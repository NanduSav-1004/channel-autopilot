"""Make one Plotline Data video locally, for review (nothing is uploaded).
Usage: python scripts/plotline_pilot.py OUT_DIR [--script-only]"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from autopilot import env, plotline


def main() -> None:
    env.load_env(ROOT / ".env")
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    with plotline.data_quota():
        plan_path, script_path = out / "plan.json", out / "script.json"
        plan = json.loads(plan_path.read_text()) if plan_path.exists() else plotline.pick_topic()
        plan_path.write_text(json.dumps(plan, indent=1))
        print("[plotline] topic:", plan["title"], "|", plan.get("angle"), "| data:", plan["series"], plan.get("states"), plan.get("owid"))
        bundle = plotline.gather(plan)
        print(f"[plotline] {len(bundle['facts'])} facts")
        script = json.loads(script_path.read_text()) if script_path.exists() else plotline.write_script(plan, bundle, draft_path=out / "draft.json")
        script_path.write_text(json.dumps(script, indent=1))
        words = sum(len(s["narration"].split()) for s in script["scenes"])
        print(f"[plotline] script: {script['title']!r}, {len(script['scenes'])} scenes, {words} words")
    if "--script-only" not in sys.argv:
        print("[plotline] video:", plotline.make_video(script, bundle, out))


if __name__ == "__main__":
    main()
