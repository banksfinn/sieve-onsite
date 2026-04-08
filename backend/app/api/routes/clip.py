from fastapi import APIRouter

from database_manager.blueprints.base_entity import BaseEntitySearchResponse
from user_management.api.dependencies import UserDependency

from app.blueprints.clip import Clip, ClipCreateRequest, ClipQuery
from app.stores.clip import clip_store

router = APIRouter()


@router.get("", response_model=BaseEntitySearchResponse[Clip])
async def search_clips(user: UserDependency, query: ClipQuery = ClipQuery()):
    return await clip_store.search_entities(query)


@router.get("/{clip_id}", response_model=Clip)
async def get_clip(user: UserDependency, clip_id: int):
    return await clip_store.get_entity_by_id(clip_id)


@router.post("", response_model=Clip)
async def create_clip(user: UserDependency, request: ClipCreateRequest):
    return await clip_store.create_entity(request)
