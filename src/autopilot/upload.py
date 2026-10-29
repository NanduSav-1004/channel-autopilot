"""YouTube upload (videos.insert, resumable) and custom thumbnails, as separate retryable steps."""
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from autopilot.metadata import EDU_CATEGORY, clean_tags, clean_title
from autopilot.youtube_auth import load_credentials


def _client(profile: str = "en"):
    return build("youtube", "v3", credentials=load_credentials(profile))


def insert_video(
    video: Path, title: str, description: str, tags: list[str],
    privacy: str = "private", publish_at: str | None = None, profile: str = "en", language: str | None = None,
) -> str:
    """Upload the video and return its id. `publish_at` (RFC 3339 UTC) schedules it as private first."""
    status = {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}
    if publish_at:
        status.update({"privacyStatus": "private", "publishAt": publish_at})
    snippet = {"title": clean_title(title), "description": description,
               "tags": clean_tags(tags), "categoryId": EDU_CATEGORY}
    if language:
        snippet.update({"defaultLanguage": language, "defaultAudioLanguage": language})
    req = _client(profile).videos().insert(
        part="snippet,status",
        body={
            "snippet": snippet,
            "status": status,
        },
        media_body=MediaFileUpload(str(video), resumable=True, chunksize=8 * 1024 * 1024),
    )
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    return resp["id"]


def set_thumbnail(video_id: str, thumbnail: Path, profile: str = "en") -> None:
    _client(profile).thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(thumbnail))).execute()


def delete_video(video_id: str, profile: str = "en") -> None:
    _client(profile).videos().delete(id=video_id).execute()
