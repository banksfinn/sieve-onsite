from datetime import UTC, datetime
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException
from user_management.blueprints.user import User
from user_management.core.security import decode_access_token
from user_management.schemas.token import TokenDependency
from user_management.stores.user import user_store


async def get_current_user(token: TokenDependency) -> User:
    access_data = decode_access_token(token)

    if datetime.fromtimestamp(access_data.exp, UTC) < datetime.now(UTC):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Token has expired")

    user = await user_store.get_entity_by_id(access_data.user_id)
    if not user:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Authentication failed, user not found")

    if access_data.impersonated_by is not None:
        user.impersonated_by = access_data.impersonated_by

    return user


UserDependency = Annotated[User, Depends(get_current_user)]
