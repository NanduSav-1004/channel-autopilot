"""Put a correction note at the top of a video's description (read-modify-write, so nothing else about the video changes).
Usage: python scripts/add_correction.py PROFILE VIDEO_ID TEXT_FILE"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from autopilot import env
from autopilot.upload import _client

LIMIT = 4990        # YouTube allows 5,000 characters in a description


def make_room(description: str, note: str) -> str:
    """Note on top. A description at the limit loses credit lines from the END of its credits list (it already ends with "...and N more"
    and a pointer to the source pages); the count in that last line grows by the number removed."""
    lines = (note + "\n\n" + description).split("\n")
    tail = re.match(r"^(\.\.\.and )(\d+)( more.*)$", lines[-1])
    removed = 0
    while sum(len(x) + 1 for x in lines) > LIMIT and tail and len(lines) > 12:
        lines.pop(-2)
        removed += 1
    if tail and removed:
        lines[-1] = f"{tail.group(1)}{int(tail.group(2)) + removed}{tail.group(3)}"
    return "\n".join(lines)


def main() -> None:
    profile, vid, text = sys.argv[1], sys.argv[2], Path(sys.argv[3]).read_text(encoding="utf-8").strip()
    env.load_env(ROOT / ".env")
    yt = _client(profile)
    item = yt.videos().list(part="snippet", id=vid).execute()["items"][0]
    snip = item["snippet"]
    if text.split("\n")[0] in snip["description"]:
        print(vid, "already has this correction")
        return
    snip["description"] = make_room(snip["description"], text)
    if len(snip["description"]) > 5000:
        raise SystemExit(f"{vid}: still {len(snip['description'])} characters, not updated")
    body = {"id": vid, "snippet": {k: snip[k] for k in ("title", "description", "categoryId", "tags", "defaultLanguage", "defaultAudioLanguage") if k in snip}}
    yt.videos().update(part="snippet", body=body).execute()
    print(vid, "description updated:", snip["description"][:90].replace("\n", " "))


if __name__ == "__main__":
    main()
