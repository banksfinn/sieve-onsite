from fastapi import APIRouter, Response
from google.auth.transport import requests
from google.oauth2 import id_token
from logging_manager.logger import get_logger
from oauth_manager.core.settings import google_oauth_settings
from user_management.blueprints.user import UserCreateRequest, UserQuery
from user_management.core.security import generate_access_token, set_access_token_cookie
from user_management.stores.user import user_store

from app.schemas.authentication.google import GoogleCredentialRequest, GoogleLoginResponse

router = APIRouter()
logger = get_logger()


@router.post("/login", response_model=GoogleLoginResponse)
async def google_login(request: GoogleCredentialRequest, response: Response) -> GoogleLoginResponse:
    """
    Authenticate a user with a Google ID token from Google One Tap / Sign-In.

    The credential is a JWT ID token that needs to be verified with Google.
    Creates a new user if they don't exist, then sets auth cookie.
    """
    try:
        # Verify the ID token with Google
        idinfo = id_token.verify_oauth2_token(  # type: ignore[reportUnknownMemberType]
            request.credential,
            requests.Request(),
            google_oauth_settings.GOOGLE_CLIENT_ID,
        )

        email = idinfo.get("email")
        name = idinfo.get("name", "")

        # Check if user already exists
        existing_users = await user_store.search_entities(UserQuery(email_address=email))

        if existing_users.entities:
            user = existing_users.entities[0]
        else:
            # Create new user
            user = await user_store.create_entity(UserCreateRequest(email_address=email, name=name))
            logger.info("Created new user", user_id=user.id, email=email)

        # Generate access token and set cookie
        access_token = generate_access_token(user.id)
        set_access_token_cookie(response, access_token)

        return GoogleLoginResponse(
            success=True,
            email=email,
            message="Successfully authenticated",
        )

    except ValueError as e:
        logger.error("Google token verification failed", error=str(e))
        return GoogleLoginResponse(
            success=False,
            message="Invalid Google token",
        )
