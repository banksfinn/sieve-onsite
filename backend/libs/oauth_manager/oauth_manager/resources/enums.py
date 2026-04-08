from enum import Enum


class OAuthProvider(str, Enum):
    """Supported OAuth providers."""

    GOOGLE = "google"


class GoogleScope(str, Enum):
    """Google OAuth scopes."""

    OPENID = "openid"
    EMAIL = "email"
    PROFILE = "profile"
