"""Re-voice and re-score an existing Short so voice and music options can be compared on the same video.

usage: python scripts/make_voice_demo.py <short_dir> <out.mp4> <engine:kokoro|piper> <voice> <speed> <music:upbeat|lofi|pulse|ambient>
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, "src")
from autopilot import audio, music, tts
from autopilot.render import render_short

short_dir, out, engine_name, voice, speed, style = Path(sys.argv[1]), Path(sys.argv[2]), *sys.argv[3:7]
script = json.loads((short_dir / "script.json").read_text())
engine = tts.make_engine({"voice_engine": engine_name, "voice_name": voice, "voice_speed": float(speed)})
work = Path("work") / ("demo_" + out.stem)
work.mkdir(parents=True, exist_ok=True)
timings = tts.synthesize_script({"sections": [{"heading": script["title"], "narration": script["narration"]}]}, work / "n.wav", engine)
dur = timings[-1]["end"]
mus = music.generate_beat(dur + 3, work / "m.wav", seed=9, style=style) if style in music.STYLES else audio.generate_ambient(dur + 3, work / "m.wav", seed=9)
parent = short_dir.parent
sections = json.loads((parent / "items.json").read_text())
from autopilot.shots import short_media_pool

pool = short_media_pool(sections, script["section_index"])
items = [{"kind": i["kind"], "path": Path(i["path"])} for i in pool if Path(i["path"]).exists()]
render_short(script, timings, items, work / "n.wav", out, work / "r", music=mus)
print(f"{out.name}: {dur:.1f}s narration, engine={engine.name} voice={voice} x{speed}, music={style}")
