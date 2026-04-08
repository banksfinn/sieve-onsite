from database_manager.blueprints.base_entity import BaseEntityDeleteRequest
from database_manager.store.base_store import BaseEntityStore
from sqlalchemy.sql import Select

from app.blueprints.video import (
    Video,
    VideoCreateRequest,
    VideoModel,
    VideoQuery,
    VideoUpdateRequest,
)


class VideoStore(
    BaseEntityStore[
        VideoModel,
        Video,
        VideoQuery,
        VideoCreateRequest,
        VideoUpdateRequest,
        BaseEntityDeleteRequest,
    ]
):
    entity_model = VideoModel
    entity = Video
    entity_query = VideoQuery
    entity_create_request = VideoCreateRequest
    entity_update_request = VideoUpdateRequest
    entity_delete_request = BaseEntityDeleteRequest

    def _apply_entity_specific_search(self, query: VideoQuery, stmt: Select[tuple[VideoModel]]) -> Select[tuple[VideoModel]]:
        if query.delivery_id:
            stmt = stmt.filter(VideoModel.delivery_id == query.delivery_id)
        if query.source:
            stmt = stmt.filter(VideoModel.source == query.source)
        if query.language:
            stmt = stmt.filter(VideoModel.language == query.language)
        return stmt


video_store = VideoStore()
