"""Build the Science Chaya monsoon pilot: voice (chaya.speak), animation (motion.js scene "monsoon"), music, sound effects, loudness, mux.
usage: python chaya/build_monsoon.py <work folder> [--no-voice]   (voice is reused from <work>/narration.wav + timings.json if --no-voice)"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from autopilot import audio, chaya, env, motion, render, sfx

root = Path(__file__).resolve().parent / "monsoon"
work = Path(sys.argv[1])
work.mkdir(parents=True, exist_ok=True)
env.load_env(Path(__file__).resolve().parents[1] / ".env")
script = json.loads((root / "script.json").read_text())
wav, tpath = work / "narration.wav", work / "timings.json"
if "--no-voice" in sys.argv and wav.exists() and tpath.exists():
    timings = json.loads(tpath.read_text())
else:
    timings = chaya.speak(script, wav)
    tpath.write_text(json.dumps(timings, ensure_ascii=False, indent=1))
sents = timings[0]["sentences"]
marks = [s["start"] for s in sents]
voice_end = sents[-1]["end"]
total = voice_end + 3.2                                   # the brand and the chai glass stay a moment after the last word
spec = {"type": "monsoon", "duration": total, "marks": marks, "canvas": [1080, 1920], "width": 1080, "height": 1920, "grain": False}
video = work / "scene.mp4"
if "--no-render" not in sys.argv:
    motion.render_scene(spec, video, fps=24)
# sound: music bed, then the voice on top (ducked), then a few effects under it
music = audio.generate_ambient(total + 2, work / "music.wav", seed=7, mood="curious")
mixed = work / "mix.wav"
print("mix:", render.mix_audio(wav, music, mixed))
ev = [(0.0, "whoosh", 0.5), (marks[4] + 1.0, "swish:3.5", 0.45), (marks[6] + 0.1, "pop", 0.5), (marks[7] + 0.1, "pop", 0.5), (marks[8] + 0.2, "swish:5.0", 0.5), (marks[10] + 0.1, "accent", 0.8)]
ev += [(marks[i], "pop", 0.3) for i in (1, 2, 3, 5, 9)]
track = sfx.render_track(ev, total, work / "sfx.wav")
withfx = sfx.add_to_mix(mixed, track, work / "mix_sfx.wav")
render.master_loudness(withfx)
final = work / "chaya_monsoon_pilot.mp4"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(withfx), "-filter_complex", "[1:a]apad[a]", "-map", "0:v", "-map", "[a]",
                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.2f}", str(final)], check=True)
print("done:", final, f"{total:.1f}s")
