from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException
from user_management.api.dependencies import UserDependency
from user_management.blueprints.user import User

from app.schemas.enums import AccessLevel, UserRole


def require_role(*allowed_roles: UserRole):
    def check(user: UserDependency) -> User:
        if user.role not in [r.value for r in allowed_roles]:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Insufficient role")
        return user

    return check


def require_admin(user: UserDependency) -> User:
    if user.access_level != AccessLevel.admin.value:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Admin access required")
    return user


AdminDependency = Annotated[User, Depends(require_admin)]
GtmOrResearchDependency = Annotated[User, Depends(require_role(UserRole.gtm, UserRole.researcher))]
InternalDependency = Annotated[User, Depends(require_role(UserRole.gtm, UserRole.researcher))]
