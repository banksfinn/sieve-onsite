from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.openapi.models import OAuthFlows
from fastapi.security import OAuth2
from logging_manager.logger import get_logger
from pydantic import BaseModel
from user_management.core.settings import settings

logger = get_logger()


class TokenEncoding(BaseModel):
    """
    This all of the data that we encode into the token.
    """

    user_id: int
    exp: float
    impersonated_by: int | None = None


class OAuth2BearerCookie(OAuth2):
    """
    This is a custom OAuth2 bearer token with cookie support.

    This is used to authenticate requests that come from the frontend using first party cookies.
    """

    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str | None = None,
        scopes: dict[str, str] | None = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlows(password={"tokenUrl": tokenUrl, "scopes": scopes})  # type: ignore
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> str | None:
        # First try to get the token from the cookie
        token = request.cookies.get(settings.TOKEN_KEY_IDENTIFIER)

        if token:
            return token

        if self.auto_error:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            return None


reusable_oauth2 = OAuth2BearerCookie(tokenUrl="/login/token")
TokenDependency = Annotated[str, Depends(reusable_oauth2)]
