from database_manager.blueprints.base_entity import BaseEntityDeleteRequest
from database_manager.store.base_store import BaseEntityStore
from sqlalchemy.sql import Select

from app.blueprints.dataset_review import (
    DatasetReview,
    DatasetReviewCreateRequest,
    DatasetReviewModel,
    DatasetReviewQuery,
    DatasetReviewReply,
    DatasetReviewReplyCreateRequest,
    DatasetReviewReplyModel,
    DatasetReviewReplyQuery,
    DatasetReviewReplyUpdateRequest,
    DatasetReviewUpdateRequest,
)


class DatasetReviewStore(
    BaseEntityStore[
        DatasetReviewModel,
        DatasetReview,
        DatasetReviewQuery,
        DatasetReviewCreateRequest,
        DatasetReviewUpdateRequest,
        BaseEntityDeleteRequest,
    ]
):
    entity_model = DatasetReviewModel
    entity = DatasetReview
    entity_query = DatasetReviewQuery
    entity_create_request = DatasetReviewCreateRequest
    entity_update_request = DatasetReviewUpdateRequest
    entity_delete_request = BaseEntityDeleteRequest

    def _apply_entity_specific_search(
        self, query: DatasetReviewQuery, stmt: Select[tuple[DatasetReviewModel]]
    ) -> Select[tuple[DatasetReviewModel]]:
        if query.dataset_id is not None:
            stmt = stmt.filter(DatasetReviewModel.dataset_id == query.dataset_id)
        if query.dataset_version_id is not None:
            stmt = stmt.filter(DatasetReviewModel.dataset_version_id == query.dataset_version_id)
        if query.clip_id is not None:
            stmt = stmt.filter(DatasetReviewModel.clip_id == query.clip_id)
        if query.user_id is not None:
            stmt = stmt.filter(DatasetReviewModel.user_id == query.user_id)
        if query.status is not None:
            stmt = stmt.filter(DatasetReviewModel.status == query.status.value)
        if query.review_type is not None:
            stmt = stmt.filter(DatasetReviewModel.review_type == query.review_type.value)
        return stmt


class DatasetReviewReplyStore(
    BaseEntityStore[
        DatasetReviewReplyModel,
        DatasetReviewReply,
        DatasetReviewReplyQuery,
        DatasetReviewReplyCreateRequest,
        DatasetReviewReplyUpdateRequest,
        BaseEntityDeleteRequest,
    ]
):
    entity_model = DatasetReviewReplyModel
    entity = DatasetReviewReply
    entity_query = DatasetReviewReplyQuery
    entity_create_request = DatasetReviewReplyCreateRequest
    entity_update_request = DatasetReviewReplyUpdateRequest
    entity_delete_request = BaseEntityDeleteRequest

    def _apply_entity_specific_search(
        self, query: DatasetReviewReplyQuery, stmt: Select[tuple[DatasetReviewReplyModel]]
    ) -> Select[tuple[DatasetReviewReplyModel]]:
        if query.review_id is not None:
            stmt = stmt.filter(DatasetReviewReplyModel.review_id == query.review_id)
        return stmt


dataset_review_store = DatasetReviewStore()
dataset_review_reply_store = DatasetReviewReplyStore()
