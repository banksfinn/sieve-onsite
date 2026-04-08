import httpx

from oauth_manager.clients.logger import get_logger
from oauth_manager.schemas.google import GoogleUserInfo


class GoogleUserClient:
    """
    Client for authenticated Google API operations.

    Use this client to make API calls on behalf of an authenticated user.
    """

    USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

    def __init__(self, access_token: str):
        """
        Initialize the client with an access token.

        Args:
            access_token: A valid Google OAuth access token
        """
        self.access_token = access_token
        self.logger = get_logger()

    def get_user_info(self) -> GoogleUserInfo:
        """
        Fetch the authenticated user's profile information from Google.

        Returns:
            GoogleUserInfo containing the user's Google ID, email, name, and picture
        """
        headers = {"Authorization": f"Bearer {self.access_token}"}

        with httpx.Client() as client:
            response = client.get(self.USERINFO_URL, headers=headers)
            response.raise_for_status()
            data = response.json()

        user_info = GoogleUserInfo(
            google_id=data["id"],
            email=data["email"],
            name=data.get("name"),
            picture=data.get("picture"),
        )

        self.logger.info(
            "Fetched Google user info",
            google_id=user_info.google_id,
            email=user_info.email,
        )

        return user_info
