from fastapi import APIRouter, Response

from database_manager.blueprints.base_entity import BaseEntitySearchResponse
from user_management.api.dependencies import UserDependency
from user_management.blueprints.user import User, UserQuery
from user_management.core.security import generate_access_token, set_access_token_cookie
from user_management.stores.user import user_store

from app.api.dependencies.authorization import GtmOrResearchDependency

router = APIRouter()


@router.get("/all", response_model=BaseEntitySearchResponse[User])
async def list_all_users(user: GtmOrResearchDependency, query: UserQuery = UserQuery()):
    return await user_store.search_entities(query)


@router.get("/me", response_model=User)
async def get_me(user: UserDependency) -> User:
    return user


@router.post("/refresh", response_model=User)
async def refresh_token(user: UserDependency, response: Response) -> User:
    access_token = generate_access_token(user.id, impersonated_by=user.impersonated_by)
    set_access_token_cookie(response, access_token)
    return user
