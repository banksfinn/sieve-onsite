from fastapi import APIRouter, Response

from user_management.api.dependencies import UserDependency
from user_management.blueprints.user import User
from user_management.core.security import generate_access_token, set_access_token_cookie

router = APIRouter()


@router.get("/me", response_model=User)
async def get_me(user: UserDependency) -> User:
    return user


@router.post("/refresh", response_model=User)
async def refresh_token(user: UserDependency, response: Response) -> User:
    access_token = generate_access_token(user.id)
    set_access_token_cookie(response, access_token)
    return user
