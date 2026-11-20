"""Upload finished Science Chaya videos to the Malayalam channel (profile "ml") as private with a publish time.
usage: python chaya/upload.py <content name> <out folder> <video id> <publish time IST 'YYYY-MM-DD HH:MM'>"""
import importlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
from autopilot import env, upload

IST = timezone(timedelta(hours=5, minutes=30))
DISCLOSURE = ("ഈ വീഡിയോയുടെ സ്ക്രിപ്റ്റ് എഴുതിയത് AI സഹായത്തോടെയാണ്, ശബ്ദം കൃത്രിമമാണ് (synthetic voice). വസ്തുതകൾ ഉറവിടങ്ങളുമായി പരിശോധിച്ചിട്ടുണ്ട്.\n"
              "Scripts are written with AI assistance and the voice is synthetic; the facts are checked against sources.")
TAGS = ["science chaya", "സയൻസ് ചായ", "malayalam science", "കേരളം", "kerala", "science explained malayalam", "education"]
EXTRA = {"monsoon": ["monsoon", "മൺസൂൺ", "മഴ", "western ghats", "പശ്ചിമഘട്ടം", "rain shadow", "kerala monsoon"],
         "electricity": ["electricity", "വൈദ്യുതി", "idukki dam", "ഇടുക്കി", "current bill", "kseb"]}


def chapters(spec: dict) -> list[str]:
    out, last = [], -99
    for sc in spec["scenes"]:
        card = next((c for c in spec["cards"] if sc["t0"] - 0.3 <= c["t0"] <= sc["t1"]), None)
        if not card or sc["t0"] - last < 12:
            continue
        s = max(0, int(sc["t0"]))
        out.append(f"{s // 60}:{s % 60:02d} {card['ml']}")
        last = sc["t0"]
    if out:
        out[0] = "0:00 " + out[0].split(" ", 1)[1]
    return out if len(out) >= 3 else []


def upload_private(name: str, out: Path, vid: str, when: str | None = None) -> str:
    """Upload as private (with a publish time, IST 'YYYY-MM-DD HH:MM', when given) and set the thumbnail of a long video. Returns the YouTube id."""
    mod = importlib.import_module(f"chaya.content_{name}")
    video = next(v for v in mod.VIDEOS if v["id"] == vid)
    work = out / vid
    spec = json.loads((work / "spec.json").read_text())
    is_short = video["orient"] == "tall"
    title = video["title_ml"] if not is_short or "#Shorts" in video["title_ml"] else video["title_ml"] + " #Shorts"
    desc = [video["title_en"], ""]
    if not is_short:
        ch = chapters(spec)
        if ch:
            desc += ch + [""]
    desc += ["ഉറവിടങ്ങൾ / Sources:"] + [f"- {f}" for f in mod.FACTS] + ["", DISCLOSURE, "", "#ScienceChaya #Malayalam #Science" + (" #Shorts" if is_short else "")]
    publish = datetime.strptime(when, "%Y-%m-%d %H:%M").replace(tzinfo=IST).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if when else None
    vid_id = upload.insert_video(work / f"{vid}.mp4", title, "\n".join(desc), TAGS + EXTRA.get(name, []), publish_at=publish, profile="ml", language="ml")
    if not is_short:        # Shorts take their cover from the video
        upload.set_thumbnail(vid_id, out / f"{vid}_thumbnail.png", profile="ml")
    (work / "uploaded.json").write_text(json.dumps({"youtube_id": vid_id, "publish_at": publish, "title": title}, ensure_ascii=False, indent=1))
    return vid_id


def main() -> None:
    name, out, vid, when = sys.argv[1], Path(sys.argv[2]), sys.argv[3], sys.argv[4]
    env.load_env(ROOT / ".env")
    print("uploaded", upload_private(name, out, vid, when))


if __name__ == "__main__":
    main()
