from datetime import datetime

from pydantic import BaseModel


class GoogleUserInfo(BaseModel):
    """User information retrieved from Google."""

    google_id: str
    email: str
    name: str | None = None
    picture: str | None = None


class GoogleTokens(BaseModel):
    """OAuth tokens from Google."""

    access_token: str
    refresh_token: str | None = None
    id_token: str | None = None
    expires_at: datetime | None = None


class GoogleAuthResult(BaseModel):
    """Complete result from Google OAuth authentication."""

    user_info: GoogleUserInfo
    tokens: GoogleTokens
