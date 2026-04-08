from database_manager.blueprints.base_entity import BaseEntityDeleteRequest
from database_manager.store.base_store import BaseEntityStore
from sqlalchemy.sql import Select

from app.blueprints.clip import (
    Clip,
    ClipCreateRequest,
    ClipModel,
    ClipQuery,
    ClipUpdateRequest,
)


class ClipStore(
    BaseEntityStore[
        ClipModel,
        Clip,
        ClipQuery,
        ClipCreateRequest,
        ClipUpdateRequest,
        BaseEntityDeleteRequest,
    ]
):
    entity_model = ClipModel
    entity = Clip
    entity_query = ClipQuery
    entity_create_request = ClipCreateRequest
    entity_update_request = ClipUpdateRequest
    entity_delete_request = BaseEntityDeleteRequest

    def _apply_entity_specific_search(self, query: ClipQuery, stmt: Select[tuple[ClipModel]]) -> Select[tuple[ClipModel]]:
        if query.video_id:
            stmt = stmt.filter(ClipModel.video_id == query.video_id)
        if query.dataset_version_id:
            stmt = stmt.filter(ClipModel.dataset_version_id == query.dataset_version_id)
        return stmt


clip_store = ClipStore()
