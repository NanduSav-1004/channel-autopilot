"""Upload spike: render a 5 s test video with FFmpeg and upload it as PRIVATE.

Answers the Phase 1 risk questions: does OAuth work, does the upload succeed,
and does the video stay locked to private (unaudited API project)?
"""
import subprocess
import sys
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

sys.path.insert(0, "src")
from autopilot.youtube_auth import load_credentials

OUT = Path("output/spike.mp4")


def make_test_video() -> None:
    OUT.parent.mkdir(exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=navy:s=1280x720:d=5",
         "-f", "lavfi", "-i", "sine=frequency=440:duration=5",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(OUT)],
        check=True, capture_output=True,
    )


def main() -> None:
    privacy = "public" if "--public" in sys.argv else "private"
    make_test_video()
    yt = build("youtube", "v3", credentials=load_credentials())
    req = yt.videos().insert(
        part="snippet,status",
        body={
            "snippet": {"title": f"API upload test ({privacy})", "description": "spike", "categoryId": "28"},
            "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False},
        },
        media_body=MediaFileUpload(str(OUT), resumable=True),
    )
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    print("uploaded video id:", resp["id"])
    print("privacy status:", resp["status"]["privacyStatus"])


if __name__ == "__main__":
    main()
