from datetime import UTC, datetime, timedelta
from http import HTTPStatus

import jwt
from fastapi import HTTPException, Response
from logging_manager.logger import get_logger
from passlib.context import CryptContext
from pydantic import ValidationError
from user_management.core.settings import settings
from user_management.schemas.token import (
    TokenDependency,
    TokenEncoding,
)

logger = get_logger()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def generate_access_token(user_id: int, impersonated_by: int | None = None) -> str:
    """
    This generates a JWT token for a given user.
    If impersonated_by is set, the token records which admin is impersonating.
    """
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = TokenEncoding(
        exp=expire.timestamp(),
        user_id=user_id,
        impersonated_by=impersonated_by,
    )
    return jwt.encode(to_encode.model_dump(), settings.TOKEN_SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: TokenDependency) -> TokenEncoding:
    """
    This decodes a JWT token and returns the TokenEncoding.
    """
    try:
        payload = jwt.decode(token, settings.TOKEN_SECRET_KEY, algorithms=[ALGORITHM])
        parsed_token = TokenEncoding.model_validate(payload)
    except ValidationError as e:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Could not validate credentials",
        ) from e
    return parsed_token


def set_access_token_cookie(response: Response, token: str) -> None:
    """Set the access token as an HTTP-only cookie."""
    response.set_cookie(
        key=settings.TOKEN_KEY_IDENTIFIER,
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",  # Protect against CSRF
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert minutes to seconds
        path="/",  # Cookie valid for all paths
        domain=settings.cookie_domain,  # Explicit domain in deployed environments for Safari compatibility
    )


def clear_access_token_cookie(response: Response) -> None:
    """Clear the access token cookie."""
    response.delete_cookie(
        key=settings.TOKEN_KEY_IDENTIFIER,
        path="/",
        secure=True,
        httponly=True,
        domain=settings.cookie_domain,
    )
