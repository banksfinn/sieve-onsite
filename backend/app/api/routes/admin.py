from fastapi import APIRouter

from database_manager.blueprints.base_entity import BaseEntitySearchResponse
from user_management.api.dependencies import UserDependency
from user_management.blueprints.user import User, UserQuery, UserUpdateRequest
from user_management.stores.user import user_store

from app.api.dependencies.authorization import AdminDependency
from app.blueprints.invitation import Invitation, InvitationCreateRequest, InvitationQuery
from app.stores.invitation import invitation_store

router = APIRouter()


@router.get("/users", response_model=BaseEntitySearchResponse[User])
async def list_users(admin: AdminDependency, query: UserQuery = UserQuery()):
    return await user_store.search_entities(query)


@router.patch("/users/{user_id}", response_model=User)
async def update_user(admin: AdminDependency, user_id: int, request: UserUpdateRequest):
    request.id = user_id
    return await user_store.update_entity(request)


@router.post("/invitations", response_model=Invitation)
async def create_invitation(admin: AdminDependency, request: InvitationCreateRequest):
    request.invited_by = admin.id
    return await invitation_store.create_entity(request)


@router.get("/invitations", response_model=BaseEntitySearchResponse[Invitation])
async def list_invitations(admin: AdminDependency, query: InvitationQuery = InvitationQuery()):
    return await invitation_store.search_entities(query)
