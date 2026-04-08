from http import HTTPStatus

from database_manager.blueprints.base_entity import BaseEntityDeleteRequest, BaseEntitySearchResponse
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

from app.blueprints.tag import Tag, TagCreateRequest, TagQuery, TagUpdateRequest
from app.blueprints.tag_member import TagMember, TagMemberCreateRequest, TagMemberUpdateRequest
from app.stores.tag import tag_store
from app.stores.tag_member import tag_member_store
from user_management.api.dependencies import UserDependency
from user_management.blueprints.user import User, UserQuery
from user_management.stores.user import user_store

router = APIRouter()


# Tag CRUD
@router.get("/")
async def get_tags(user: UserDependency) -> BaseEntitySearchResponse[Tag]:
    """Get all tags the user has access to."""
    return await tag_store.search_entities(TagQuery(user_id=user.id))


@router.get("/{tag_id}")
async def get_tag(user: UserDependency, tag_id: int) -> Tag:
    """Get a specific tag (must be a member)."""
    tag = await tag_store.get_entity_by_id(tag_id)
    if not tag:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Tag not found")
    # Verify user has access
    membership = await tag_member_store.get_member(tag_id, user.id)
    if not membership:
        raise HTTPException(HTTPStatus.FORBIDDEN, "Not a member of this tag")
    return tag


@router.post("/")
async def create_tag(user: UserDependency, request: TagCreateRequest) -> Tag:
    """Create a new tag. Creator automatically becomes a member with 'creator' role."""
    request.created_by = user.id
    tag = await tag_store.create_entity(request)

    # Add creator as member with their preferred color
    await tag_member_store.add_member(
        TagMemberCreateRequest(tag_id=tag.id, user_id=user.id, role="creator", color=request.color)
    )

    # Refetch to include members
    return await tag_store.get_entity_by_id(tag.id)  # type: ignore[return-value]


@router.patch("/{tag_id}")
async def update_tag(user: UserDependency, tag_id: int, request: TagUpdateRequest) -> Tag:
    """Update tag properties (name, icon). Only creator can update."""
    tag = await tag_store.get_entity_by_id(tag_id)
    if not tag:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Tag not found")

    membership = await tag_member_store.get_member(tag_id, user.id)
    if not membership or membership.role != "creator":
        raise HTTPException(HTTPStatus.FORBIDDEN, "Only tag creator can update")

    request.id = tag_id
    return await tag_store.update_entity(request)


@router.delete("/{tag_id}")
async def delete_tag(user: UserDependency, tag_id: int) -> Tag:
    """Delete a tag. Only creator can delete."""
    tag = await tag_store.get_entity_by_id(tag_id)
    if not tag:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Tag not found")

    membership = await tag_member_store.get_member(tag_id, user.id)
    if not membership or membership.role != "creator":
        raise HTTPException(HTTPStatus.FORBIDDEN, "Only tag creator can delete")

    return await tag_store.delete_entity(BaseEntityDeleteRequest(id=tag_id))


# Tag membership management
class AddMemberRequest(BaseModel):
    user_id: int


@router.post("/{tag_id}/members")
async def add_tag_member(user: UserDependency, tag_id: int, request: AddMemberRequest) -> TagMember:
    """Share tag with another user. Only existing members can share."""
    membership = await tag_member_store.get_member(tag_id, user.id)
    if not membership:
        raise HTTPException(HTTPStatus.FORBIDDEN, "Must be a member to share this tag")

    return await tag_member_store.add_member(TagMemberCreateRequest(tag_id=tag_id, user_id=request.user_id, role="member"))


@router.delete("/{tag_id}/members/{target_user_id}")
async def remove_tag_member(user: UserDependency, tag_id: int, target_user_id: int) -> None:
    """Remove a member from a tag. Creator can remove anyone; members can only leave."""
    membership = await tag_member_store.get_member(tag_id, user.id)
    if not membership:
        raise HTTPException(HTTPStatus.FORBIDDEN, "Not a member of this tag")

    if target_user_id != user.id and membership.role != "creator":
        raise HTTPException(HTTPStatus.FORBIDDEN, "Only creator can remove other members")

    if target_user_id == user.id and membership.role == "creator":
        raise HTTPException(HTTPStatus.BAD_REQUEST, "Creator cannot leave tag; delete it instead")

    await tag_member_store.remove_member(tag_id, target_user_id)


class UpdatePreferencesRequest(BaseModel):
    color: str | None = None


@router.patch("/{tag_id}/my-preferences")
async def update_my_tag_preferences(user: UserDependency, tag_id: int, request: UpdatePreferencesRequest) -> TagMember:
    """Update personal preferences for a tag (color)."""
    return await tag_member_store.update_member(TagMemberUpdateRequest(tag_id=tag_id, user_id=user.id, color=request.color))


# User listing for sharing UI (temporary - will need pagination/search later)
@router.get("/users/all")
async def get_all_users(user: UserDependency) -> BaseEntitySearchResponse[User]:
    """Get all users for tag sharing UI. Temporary - needs pagination/search."""
    return await user_store.search_entities(UserQuery(limit=100))
