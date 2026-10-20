"""YouTube OAuth: one-time interactive login, then headless use from a refresh token."""
import json
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]
CLIENT_SECRET = Path("client_secret.json")
TOKEN_PATH = Path("secrets/token.json")


def login_interactive() -> Credentials:
    """Run once on a machine with a browser. Saves the refresh token locally."""
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
    creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
    TOKEN_PATH.parent.mkdir(exist_ok=True)
    TOKEN_PATH.write_text(creds.to_json())
    return creds


def load_credentials() -> Credentials:
    """Headless. CI supplies YOUTUBE_* env vars (GitHub Secrets); locally uses the token file."""
    if os.environ.get("YOUTUBE_REFRESH_TOKEN"):
        creds = Credentials(
            token=None,
            refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"],
            client_id=os.environ["YOUTUBE_CLIENT_ID"],
            client_secret=os.environ["YOUTUBE_CLIENT_SECRET"],
            token_uri="https://oauth2.googleapis.com/token",
            scopes=SCOPES,
        )
    else:
        creds = Credentials.from_authorized_user_info(json.loads(TOKEN_PATH.read_text()), SCOPES)
    if not creds.valid:
        creds.refresh(Request())
    return creds


if __name__ == "__main__":
    login_interactive()
    print(f"Saved refresh token to {TOKEN_PATH}")
