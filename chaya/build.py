"""Build Science Chaya videos from a content file (chaya/content_<name>.py -> VIDEOS): voice, animation, music, effects, loudness, mux, check, thumbnail.
usage: python chaya/build.py <name> <out folder> [video id ...] [--no-voice] [--no-render]
Each beat of a video is ONE sentence of narration; a scene begins at the beat that carries one, and `atb` (beats counted from the scene's first beat)
inside a scene's parameters becomes the fraction of the scene at which that part starts."""
import importlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
from autopilot import audio, chaya, env, motion, qa_video, render, sfx

CHUNK = 6       # beats per voice request: a whole long narration in one request is refused or cut
TAIL = 3.6      # the brand and the chai glass stay after the last word


def convert_atb(node, beat_t, first, n_beats, t0, t1):
    """Replace every {"atb": b} with {"at": fraction of the scene}; b counts beats from the scene's first beat (fractions allowed)."""
    def frac(b):
        i = int(b)
        if first + i >= len(beat_t) - 1:
            sec = beat_t[-1] + (b - (len(beat_t) - 1 - first)) * 2.0
        else:
            sec = beat_t[first + i] + (b - i) * (beat_t[first + i + 1] - beat_t[first + i])
        return round((sec - t0) / max(0.5, t1 - t0), 4)
    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            if k == "atb" and isinstance(v, dict):
                out["at"] = {kk: frac(vv) for kk, vv in v.items()}
            elif k == "atb":
                out["at"] = frac(v)
            else:
                out[k] = convert_atb(v, beat_t, first, n_beats, t0, t1)
        return out
    if isinstance(node, list):
        return [convert_atb(v, beat_t, first, n_beats, t0, t1) for v in node]
    return node


def plan(video: dict, sents: list[dict]) -> dict:
    beats = video["beats"]
    if len(sents) != len(beats):
        raise SystemExit(f"{video['id']}: {len(beats)} beats but the voice has {len(sents)} sentences")
    starts = [s["start"] for s in sents]
    beat_t = starts + [sents[-1]["end"]]
    total = sents[-1]["end"] + TAIL
    idx = [i for i, b in enumerate(beats) if b["scene"]]
    if not idx or idx[0] != 0:
        raise SystemExit("the first beat needs a scene")
    scenes = []
    for k, i in enumerate(idx):
        t0 = starts[i] - (0.0 if i == 0 else 0.15)
        t1 = (starts[idx[k + 1]] - 0.15) if k + 1 < len(idx) else total
        sc = beats[i]["scene"]
        scenes.append({"kind": sc["kind"], "t0": round(t0, 3), "t1": round(t1, 3), "p": convert_atb(sc.get("p", {}), beat_t, i, len(beats), t0, t1)})
    cards = []
    for i, b in enumerate(beats):
        if b["card"]:
            ml, en, col = b["card"]
            end = starts[i + 1] - 0.05 if i + 1 < len(beats) else sents[i]["end"] + 0.5
            cards.append({"t0": round(starts[i] + 0.05, 3), "t1": round(end, 3), "ml": ml, "en": en, "col": col})
    size = (1920, 1080) if video["orient"] == "wide" else (1080, 1920)
    return {"type": "chaya", "duration": round(total, 3), "scenes": scenes, "cards": cards, "canvas": list(size), "width": size[0], "height": size[1], "grain": False}, starts, total


def events(spec: dict, starts: list[float], total: float):
    ev = [(0.0, "whoosh", 0.45)]
    for sc in spec["scenes"][1:]:
        ev.append((sc["t0"] + 0.05, "swish:1.2", 0.35))
    ev += [(cd["t0"], "pop", 0.22) for cd in spec["cards"]]
    ev.append((spec["scenes"][-1]["t0"] + 0.3, "accent", 0.7))
    return ev


def thumbnail(video: dict, final: Path, out_png: Path, work: Path) -> None:
    """A frame from the video at the hero scene, a warm wash, and the big Malayalam title with a small English line."""
    spec = json.loads((work / "spec.json").read_text())
    hero = next((s for s in spec["scenes"] if s["kind"] == video["thumb"]["hero"]), spec["scenes"][0])
    t = hero["t0"] + (hero["t1"] - hero["t0"]) * 0.72
    frame = work / "thumb_frame.png"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", str(final), "-frames:v", "1", str(frame)], check=True)
    wide = video["orient"] == "wide"
    w, h = (1280, 720) if wide else (1080, 1920)
    html = work / "thumb.html"
    html.write_text(f"""<html><body style="margin:0;width:{w}px;height:{h}px;overflow:hidden;position:relative;background:#f6e8d3;font-family:'Noto Sans Malayalam','Noto Sans',sans-serif">
<img src="{frame.name}" style="position:absolute;left:0;top:{'-60px' if wide else '0'};width:{w}px;height:{'auto' if wide else str(h) + 'px'};object-fit:cover;filter:saturate(1.15)">
<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(74,42,23,.05) 0%,rgba(74,42,23,.0) 40%,rgba(74,42,23,.82) 100%)"></div>
<div style="position:absolute;left:{40 if wide else 50}px;right:{40 if wide else 50}px;bottom:{34 if wide else 160}px;text-align:center">
<div style="display:inline-block;background:#c45a2a;color:#fff;font-weight:800;font-size:{104 if wide else 120}px;line-height:1.25;padding:6px 40px 14px;border-radius:34px;box-shadow:0 10px 30px rgba(0,0,0,.4)">{video['thumb']['ml']}</div>
<div style="color:#ffe9b8;font-weight:800;letter-spacing:8px;font-size:{38 if wide else 46}px;margin-top:14px;text-shadow:0 3px 10px rgba(0,0,0,.6)">{video['thumb']['en']}</div></div>
<div style="position:absolute;left:30px;top:22px;background:#fff7e8;color:#7b4a2b;font-weight:800;font-size:{40 if wide else 46}px;padding:2px 24px 8px;border-radius:26px">സയൻസ് ചായ</div>
</body></html>""")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=motion._chrome(), args=["--allow-file-access-from-files"]) if motion._chrome() else p.chromium.launch()
        pg = b.new_page(viewport={"width": w, "height": h})
        pg.goto(html.as_uri())
        pg.wait_for_timeout(600)
        pg.screenshot(path=str(out_png))
        b.close()


def speak_chunks(video: dict, work: Path, out_wav: Path) -> list[dict]:
    """The narration in groups of CHUNK beats, each saved as it is spoken (voice requests are limited per day: a retry must not repeat finished ones)."""
    import time
    import wave
    texts = [b["t"] for b in video["beats"]]
    parts, t = [], 0.0
    for n, i in enumerate(range(0, len(texts), CHUNK)):
        cw, cj = work / f"voice_{n}.wav", work / f"voice_{n}.json"
        if not (cw.exists() and cj.exists()):
            script = {"title": video["title_ml"], "sections": [{"heading": f"{video['id']}-{n}", "narration": " ".join(texts[i:i + CHUNK])}]}
            for attempt in range(40):          # one voice for the whole video: wait for the daily quota instead of switching model
                try:
                    sec = chaya.speak(script, cw, models=(chaya.MODEL,))
                    break
                except OSError as exc:
                    print(f"[chaya] waiting for voice quota ({str(exc)[:80]}); retry in 15 min", flush=True)
                    time.sleep(900)
            else:
                raise SystemExit("the voice quota did not come back")
            cj.write_text(json.dumps(sec, ensure_ascii=False))
            time.sleep(8)
        parts.append((cw, json.loads(cj.read_text())))
    timings = []
    with wave.open(str(out_wav), "wb") as o:
        for k, (cw, sec) in enumerate(parts):
            with wave.open(str(cw)) as r:
                if k == 0:
                    o.setparams(r.getparams())
                o.writeframes(r.readframes(r.getnframes()))
                dur = r.getnframes() / r.getframerate()
            for s2 in sec:
                s2["start"] += t
                s2["end"] += t
                for x in s2["sentences"]:
                    x["start"] += t
                    x["end"] += t
                    for w in x.get("words", []):
                        w["s"] += t
                        w["e"] += t
                timings.append(s2)
            t += dur
    return timings


def build(video: dict, out: Path, flags: set) -> Path:
    work = out / video["id"]
    work.mkdir(parents=True, exist_ok=True)
    wav, tpath = work / "narration.wav", work / "timings.json"
    if "--no-voice" in flags and wav.exists() and tpath.exists():
        timings = json.loads(tpath.read_text())
    else:
        timings = speak_chunks(video, work, wav)
        tpath.write_text(json.dumps(timings, ensure_ascii=False, indent=1))
    sents = [x for sec in timings for x in sec["sentences"]]
    spec, starts, total = plan(video, sents)
    (work / "spec.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1))
    clip = work / "scene.mp4"
    fps = 24
    if "--no-render" not in flags or not clip.exists():
        motion.render_scene(spec, clip, fps=fps)
    music = audio.generate_ambient(total + 2, work / "music.wav", seed=sum(map(ord, video["id"])) % 50, mood=video.get("mood", "curious"))
    mixed = work / "mix.wav"
    render.mix_audio(wav, music, mixed)
    track = sfx.render_track(events(spec, starts, total), total, work / "sfx.wav")
    withfx = sfx.add_to_mix(mixed, track, work / "mix_sfx.wav")
    render.master_loudness(withfx)
    final = work / f"{video['id']}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(clip), "-i", str(withfx), "-filter_complex", "[1:a]apad[a]", "-map", "0:v", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.2f}", str(final)], check=True)
    try:
        qa_video.gate(final, "long" if video["orient"] == "wide" else "short", tuple(spec["canvas"]))
    except Exception as exc:  # noqa: BLE001 - report, keep going: the morning review decides
        print("QA:", exc)
    thumbnail(video, final, out / f"{video['id']}_thumbnail.png", work)
    meta = {k: video.get(k) for k in ("id", "title_ml", "title_en", "comment")}
    meta["seconds"] = round(total, 1)
    meta["chapters"] = None
    (work / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    print("done:", final, f"{total:.1f}s")
    return final


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    name, out, only = args[0], Path(args[1]), set(args[2:])
    env.load_env(ROOT / ".env")
    mod = importlib.import_module(f"chaya.content_{name}")
    for v in mod.VIDEOS:
        if not only or v["id"] in only:
            build(v, out, flags)
