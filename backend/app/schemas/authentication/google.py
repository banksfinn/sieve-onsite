from pydantic import BaseModel


class GoogleCredentialRequest(BaseModel):
    """Request body for Google One Tap / Sign-In authentication."""

    credential: str


class GoogleLoginResponse(BaseModel):
    """Response from Google login."""

    success: bool
    email: str | None = None
    message: str | None = None
