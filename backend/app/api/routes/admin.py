from datetime import UTC, datetime
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from logging_manager.logger import get_logger
from pydantic import BaseModel

from database_manager.blueprints.base_entity import BaseEntitySearchResponse
from user_management.blueprints.user import User, UserCreateRequest, UserQuery, UserUpdateRequest
from user_management.core.security import decode_access_token, generate_access_token, set_access_token_cookie
from user_management.schemas.token import TokenDependency
from user_management.stores.user import user_store

from app.api.dependencies.authorization import AdminDependency
from app.blueprints.invitation import Invitation, InvitationCreateRequest, InvitationQuery
from app.schemas.enums import AccessLevel, UserRole
from app.stores.invitation import invitation_store

router = APIRouter()
logger = get_logger()


# --- User management ---


@router.get("/users", response_model=BaseEntitySearchResponse[User])
async def list_users(admin: AdminDependency, query: UserQuery = UserQuery()):
    return await user_store.search_entities(query)


@router.patch("/users/{user_id}", response_model=User)
async def update_user(admin: AdminDependency, user_id: int, request: UserUpdateRequest):
    request.id = user_id
    return await user_store.update_entity(request)


# --- Invitations ---


@router.post("/invitations", response_model=Invitation)
async def create_invitation(admin: AdminDependency, request: InvitationCreateRequest):
    request.invited_by = admin.id
    return await invitation_store.create_entity(request)


@router.get("/invitations", response_model=BaseEntitySearchResponse[Invitation])
async def list_invitations(admin: AdminDependency, query: InvitationQuery = InvitationQuery()):
    return await invitation_store.search_entities(query)


# --- Impersonation ---


class ImpersonateRequest(BaseModel):
    user_id: int


@router.post("/impersonate", response_model=User)
async def impersonate_user(admin: AdminDependency, request: ImpersonateRequest, response: Response):
    target = await user_store.get_entity_by_id(request.user_id)
    if not target:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

    if target.access_level == AccessLevel.admin.value and target.id != admin.id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Cannot impersonate another admin")

    logger.warning("Admin impersonating user", admin_id=admin.id, target_user_id=target.id)

    token = generate_access_token(user_id=target.id, impersonated_by=admin.id)
    set_access_token_cookie(response, token)
    return target


async def get_impersonating_admin(token: TokenDependency) -> User:
    """Resolve the original admin from an impersonation token. Rejects non-impersonation tokens."""
    access_data = decode_access_token(token)

    if datetime.fromtimestamp(access_data.exp, UTC) < datetime.now(UTC):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Token has expired")

    if access_data.impersonated_by is None:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Not currently impersonating")

    admin = await user_store.get_entity_by_id(access_data.impersonated_by)
    if not admin or admin.access_level != AccessLevel.admin.value:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Original admin not found or no longer admin")

    return admin


ImpersonatingAdminDependency = Annotated[User, Depends(get_impersonating_admin)]


@router.post("/stop-impersonation", response_model=User)
async def stop_impersonation(admin: ImpersonatingAdminDependency, response: Response):
    logger.info("Admin stopped impersonation", admin_id=admin.id)
    token = generate_access_token(user_id=admin.id)
    set_access_token_cookie(response, token)
    return admin


# --- Fake users for testing ---


class CreateFakeUserRequest(BaseModel):
    name: str
    email_address: str
    role: UserRole = UserRole.customer
    access_level: AccessLevel = AccessLevel.regular


@router.post("/fake-users", response_model=User)
async def create_fake_user(admin: AdminDependency, request: CreateFakeUserRequest):
    existing = await user_store.search_entities(UserQuery(email_address=request.email_address))
    if existing.entities:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="User with this email already exists")

    user = await user_store.create_entity(
        UserCreateRequest(
            email_address=request.email_address,
            name=request.name,
            role=request.role.value,
            access_level=request.access_level.value,
        )
    )
    logger.info("Created fake user", admin_id=admin.id, fake_user_id=user.id, role=request.role.value)
    return user
