from oauth_manager.clients.google.oauth_client import GoogleOAuthClient
from oauth_manager.clients.google.user_client import GoogleUserClient
from oauth_manager.schemas.google import GoogleAuthResult


def authenticate_google_user(code: str) -> GoogleAuthResult:
    """
    Complete the Google OAuth flow and return user info with tokens.

    This function should be called from your OAuth callback endpoint.
    It exchanges the authorization code for tokens and fetches the user's
    profile information from Google.

    Args:
        code: The authorization code from Google's OAuth callback

    Returns:
        GoogleAuthResult containing:
        - user_info: GoogleUserInfo with google_id, email, name, picture
        - tokens: GoogleTokens with access_token, refresh_token, id_token, expires_at

    Example:
        @router.get("/auth/google/callback")
        async def google_callback(code: str):
            result = authenticate_google_user(code)
            # Use result.user_info.email to find/create user
            # Store result.tokens.refresh_token if you need to refresh later
    """
    oauth_client = GoogleOAuthClient()
    tokens = oauth_client.exchange_code(code)

    user_client = GoogleUserClient(tokens.access_token)
    user_info = user_client.get_user_info()

    return GoogleAuthResult(user_info=user_info, tokens=tokens)


def get_google_authorization_url(state: str | None = None) -> str:
    """
    Generate the Google OAuth authorization URL.

    This function should be called when you want to initiate the OAuth flow.
    Redirect the user to the returned URL to begin the consent process.

    Args:
        state: Optional state parameter for CSRF protection.
               Will be returned in the callback.

    Returns:
        The Google OAuth authorization URL

    Example:
        @router.get("/auth/google")
        async def google_login():
            state = generate_csrf_token()
            url = get_google_authorization_url(state=state)
            return RedirectResponse(url)
    """
    oauth_client = GoogleOAuthClient()
    return oauth_client.get_authorization_url(state=state)
