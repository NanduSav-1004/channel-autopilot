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
# Posting a comment needs this one as well (the broad "youtube" scope does NOT cover commentThreads.insert). Tokens made before 2 Nov 2026 lack
# it: asking Google for a scope a token was not granted makes the refresh fail, so only the comment job asks for it (load_credentials(scopes=...)).
SCOPE_COMMENTS = "https://www.googleapis.com/auth/youtube.force-ssl"
SCOPES_WITH_COMMENTS = [*SCOPES, SCOPE_COMMENTS]
CLIENT_SECRET = Path("client_secret.json")
TOKEN_PATH = Path("secrets/token.json")
TOKEN_PATH_ML = Path("secrets/token_ml.json")     # the Malayalam channel is a separate channel with its own login
TOKEN_PATH_DATA = Path("secrets/token_data.json")  # and so is the data channel (Plotline Data)


def token_path(profile: str = "en") -> Path:
    return {"ml": TOKEN_PATH_ML, "data": TOKEN_PATH_DATA}.get(profile, TOKEN_PATH)


def login_interactive(profile: str = "en") -> Credentials:
    """Run once on a machine with a browser. Saves the refresh token locally. For the Malayalam channel choose that
    channel (or its brand account) on the Google consent screen."""
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES_WITH_COMMENTS)
    creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
    token_path(profile).parent.mkdir(exist_ok=True)
    token_path(profile).write_text(creds.to_json())
    return creds


def configured(profile: str = "en") -> bool:
    """Is there a login for this channel (CI secret or local token file)?"""
    return bool(os.environ.get(_refresh_env(profile))) or token_path(profile).exists()


def _refresh_env(profile: str) -> str:
    return {"ml": "YOUTUBE_REFRESH_TOKEN_ML", "data": "YOUTUBE_REFRESH_TOKEN_DATA"}.get(profile, "YOUTUBE_REFRESH_TOKEN")


def load_credentials(profile: str = "en", scopes: list[str] | None = None) -> Credentials:
    """Headless. CI supplies YOUTUBE_* env vars (GitHub Secrets); locally uses the token file. `scopes` defaults to SCOPES (what every token has)."""
    scopes = scopes or SCOPES
    if os.environ.get(_refresh_env(profile)):
        creds = Credentials(
            token=None,
            refresh_token=os.environ[_refresh_env(profile)],
            client_id=os.environ["YOUTUBE_CLIENT_ID"],
            client_secret=os.environ["YOUTUBE_CLIENT_SECRET"],
            token_uri="https://oauth2.googleapis.com/token",
            scopes=scopes,
        )
    else:
        creds = Credentials.from_authorized_user_info(json.loads(token_path(profile).read_text()), scopes)
    if not creds.valid:
        creds.refresh(Request())
    return creds


if __name__ == "__main__":
    import sys

    prof = "ml" if "--ml" in sys.argv else "data" if "--data" in sys.argv else "en"
    login_interactive(prof)
    print(f"Saved refresh token to {token_path(prof)}")
