from database_manager.blueprints.base_entity import BaseEntityDeleteRequest
from database_manager.store.base_store import BaseEntityStore
from sqlalchemy.sql import Select

from app.blueprints.delivery_feedback import (
    DeliveryFeedback,
    DeliveryFeedbackCreateRequest,
    DeliveryFeedbackModel,
    DeliveryFeedbackQuery,
    DeliveryFeedbackUpdateRequest,
)


class DeliveryFeedbackStore(
    BaseEntityStore[
        DeliveryFeedbackModel,
        DeliveryFeedback,
        DeliveryFeedbackQuery,
        DeliveryFeedbackCreateRequest,
        DeliveryFeedbackUpdateRequest,
        BaseEntityDeleteRequest,
    ]
):
    entity_model = DeliveryFeedbackModel
    entity = DeliveryFeedback
    entity_query = DeliveryFeedbackQuery
    entity_create_request = DeliveryFeedbackCreateRequest
    entity_update_request = DeliveryFeedbackUpdateRequest
    entity_delete_request = BaseEntityDeleteRequest

    def _apply_entity_specific_search(
        self, query: DeliveryFeedbackQuery, stmt: Select[tuple[DeliveryFeedbackModel]]
    ) -> Select[tuple[DeliveryFeedbackModel]]:
        if query.delivery_id:
            stmt = stmt.filter(DeliveryFeedbackModel.delivery_id == query.delivery_id)
        if query.user_id:
            stmt = stmt.filter(DeliveryFeedbackModel.user_id == query.user_id)
        return stmt


delivery_feedback_store = DeliveryFeedbackStore()
