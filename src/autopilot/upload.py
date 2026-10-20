"""YouTube upload (videos.insert, resumable) plus custom thumbnail."""
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from autopilot.metadata import EDU_CATEGORY, clean_tags, clean_title
from autopilot.youtube_auth import load_credentials


def upload_video(
    video: Path, title: str, description: str, tags: list[str], thumbnail: Path | None = None,
    privacy: str = "private", publish_at: str | None = None,
) -> str:
    """Return the new video id. `publish_at` (RFC 3339 UTC) schedules it; requires privacy 'private'."""
    yt = build("youtube", "v3", credentials=load_credentials())
    status = {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}
    if publish_at:
        status.update({"privacyStatus": "private", "publishAt": publish_at})
    req = yt.videos().insert(
        part="snippet,status",
        body={
            "snippet": {"title": clean_title(title), "description": description,
                        "tags": clean_tags(tags), "categoryId": EDU_CATEGORY},
            "status": status,
        },
        media_body=MediaFileUpload(str(video), resumable=True, chunksize=8 * 1024 * 1024),
    )
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    if thumbnail:
        yt.thumbnails().set(videoId=resp["id"], media_body=MediaFileUpload(str(thumbnail))).execute()
    return resp["id"]
