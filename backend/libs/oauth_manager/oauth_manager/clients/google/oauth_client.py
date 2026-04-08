from datetime import timezone

from google_auth_oauthlib.flow import Flow  # type: ignore
from oauth_manager.clients.logger import get_logger
from oauth_manager.core.settings import google_oauth_settings
from oauth_manager.schemas.google import GoogleTokens


class GoogleOAuthClient:
    """
    Client for unauthenticated Google OAuth operations.

    Use this client to:
    - Generate authorization URLs for the OAuth consent flow
    - Exchange authorization codes for access tokens
    """

    def __init__(self):
        self.logger = get_logger()
        self.client_config = {
            "web": {
                "client_id": google_oauth_settings.GOOGLE_CLIENT_ID,
                "client_secret": google_oauth_settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }
        self.scopes = google_oauth_settings.GOOGLE_SCOPES
        self.redirect_uri = google_oauth_settings.GOOGLE_REDIRECT_URI

    def _create_flow(self) -> Flow:
        """Create a new OAuth flow instance."""
        flow = Flow.from_client_config(  # type: ignore
            self.client_config,
            scopes=self.scopes,
            redirect_uri=self.redirect_uri,
        )
        return flow

    def get_authorization_url(self, state: str | None = None) -> str:
        """
        Generate the Google OAuth consent URL.

        Args:
            state: Optional state parameter for CSRF protection

        Returns:
            The authorization URL to redirect the user to
        """
        flow = self._create_flow()
        authorization_url, _ = flow.authorization_url(  # type: ignore
            access_type="offline",
            include_granted_scopes="true",
            state=state,
            prompt="consent",
        )
        self.logger.info("Generated Google authorization URL", state=state)
        return authorization_url  # type: ignore

    def exchange_code(self, code: str) -> GoogleTokens:
        """
        Exchange an authorization code for access tokens.

        Args:
            code: The authorization code from the OAuth callback

        Returns:
            GoogleTokens containing access_token, refresh_token, etc.
        """
        flow = self._create_flow()
        flow.fetch_token(code=code)  # type: ignore

        credentials = flow.credentials

        expires_at = None
        if credentials.expiry:  # type: ignore
            expires_at = credentials.expiry.replace(tzinfo=timezone.utc)  # type: ignore

        # credentials.token should always be set after fetch_token succeeds
        access_token = credentials.token  # type: ignore
        if not isinstance(access_token, str):
            raise ValueError("Expected access_token to be a string after token exchange")

        # id_token is available on OAuth2 credentials but not typed
        id_token = getattr(credentials, "id_token", None)

        tokens = GoogleTokens(
            access_token=access_token,
            refresh_token=credentials.refresh_token,  # type: ignore
            id_token=id_token,
            expires_at=expires_at,  # type: ignore
        )

        self.logger.info(
            "Exchanged authorization code for tokens",
            has_refresh_token=tokens.refresh_token is not None,
        )

        return tokens
