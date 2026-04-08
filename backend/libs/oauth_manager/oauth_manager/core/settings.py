import os

from pydantic_settings import BaseSettings


class GoogleOAuthSettings(BaseSettings):
    """Configuration for Google OAuth."""

    GOOGLE_CLIENT_ID: str = os.environ.get("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.environ.get("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.environ["FRONTEND_URL"] + "/api/gateway/auth/google/callback"
    GOOGLE_SCOPES: list[str] = ["openid", "email", "profile"]
    FRONTEND_URL: str = os.environ.get("FRONTEND_URL", "http://localhost:6011")


google_oauth_settings = GoogleOAuthSettings()
