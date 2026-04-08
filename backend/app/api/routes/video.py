from fastapi import APIRouter

from database_manager.blueprints.base_entity import BaseEntitySearchResponse
from user_management.api.dependencies import UserDependency

from app.blueprints.video import Video, VideoCreateRequest, VideoQuery
from app.stores.video import video_store

router = APIRouter()


@router.get("", response_model=BaseEntitySearchResponse[Video])
async def search_videos(user: UserDependency, query: VideoQuery = VideoQuery()):
    return await video_store.search_entities(query)


@router.get("/{video_id}", response_model=Video)
async def get_video(user: UserDependency, video_id: int):
    return await video_store.get_entity_by_id(video_id)


@router.post("", response_model=Video)
async def create_video(user: UserDependency, request: VideoCreateRequest):
    return await video_store.create_entity(request)
