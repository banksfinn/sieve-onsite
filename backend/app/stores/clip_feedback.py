from database_manager.blueprints.base_entity import BaseEntityDeleteRequest
from database_manager.store.base_store import BaseEntityStore
from sqlalchemy.sql import Select

from app.blueprints.clip_feedback import (
    ClipFeedback,
    ClipFeedbackCreateRequest,
    ClipFeedbackModel,
    ClipFeedbackQuery,
    ClipFeedbackUpdateRequest,
)


class ClipFeedbackStore(
    BaseEntityStore[
        ClipFeedbackModel,
        ClipFeedback,
        ClipFeedbackQuery,
        ClipFeedbackCreateRequest,
        ClipFeedbackUpdateRequest,
        BaseEntityDeleteRequest,
    ]
):
    entity_model = ClipFeedbackModel
    entity = ClipFeedback
    entity_query = ClipFeedbackQuery
    entity_create_request = ClipFeedbackCreateRequest
    entity_update_request = ClipFeedbackUpdateRequest
    entity_delete_request = BaseEntityDeleteRequest

    def _apply_entity_specific_search(
        self, query: ClipFeedbackQuery, stmt: Select[tuple[ClipFeedbackModel]]
    ) -> Select[tuple[ClipFeedbackModel]]:
        if query.clip_id:
            stmt = stmt.filter(ClipFeedbackModel.clip_id == query.clip_id)
        if query.delivery_id:
            stmt = stmt.filter(ClipFeedbackModel.delivery_id == query.delivery_id)
        if query.user_id:
            stmt = stmt.filter(ClipFeedbackModel.user_id == query.user_id)
        return stmt


clip_feedback_store = ClipFeedbackStore()
