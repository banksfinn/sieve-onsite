from database_manager.blueprints.base_entity import BaseEntityDeleteRequest
from database_manager.store.base_store import BaseEntityStore
from sqlalchemy.sql import Select

from app.blueprints.dataset import (
    Dataset,
    DatasetCreateRequest,
    DatasetModel,
    DatasetQuery,
    DatasetUpdateRequest,
    DatasetVersion,
    DatasetVersionCreateRequest,
    DatasetVersionModel,
    DatasetVersionQuery,
    DatasetVersionUpdateRequest,
    DatasetVersionVideo,
    DatasetVersionVideoCreateRequest,
    DatasetVersionVideoModel,
    DatasetVersionVideoQuery,
)


class DatasetStore(
    BaseEntityStore[
        DatasetModel,
        Dataset,
        DatasetQuery,
        DatasetCreateRequest,
        DatasetUpdateRequest,
        BaseEntityDeleteRequest,
    ]
):
    entity_model = DatasetModel
    entity = Dataset
    entity_query = DatasetQuery
    entity_create_request = DatasetCreateRequest
    entity_update_request = DatasetUpdateRequest
    entity_delete_request = BaseEntityDeleteRequest

    def _apply_entity_specific_search(self, query: DatasetQuery, stmt: Select[tuple[DatasetModel]]) -> Select[tuple[DatasetModel]]:
        if query.name:
            stmt = stmt.filter(DatasetModel.name.ilike(f"%{query.name}%"))
        if query.status:
            stmt = stmt.filter(DatasetModel.status == query.status)
        return stmt


class DatasetVersionStore(
    BaseEntityStore[
        DatasetVersionModel,
        DatasetVersion,
        DatasetVersionQuery,
        DatasetVersionCreateRequest,
        DatasetVersionUpdateRequest,
        BaseEntityDeleteRequest,
    ]
):
    entity_model = DatasetVersionModel
    entity = DatasetVersion
    entity_query = DatasetVersionQuery
    entity_create_request = DatasetVersionCreateRequest
    entity_update_request = DatasetVersionUpdateRequest
    entity_delete_request = BaseEntityDeleteRequest

    def _apply_entity_specific_search(
        self, query: DatasetVersionQuery, stmt: Select[tuple[DatasetVersionModel]]
    ) -> Select[tuple[DatasetVersionModel]]:
        if query.dataset_id:
            stmt = stmt.filter(DatasetVersionModel.dataset_id == query.dataset_id)
        return stmt


class DatasetVersionVideoStore(
    BaseEntityStore[
        DatasetVersionVideoModel,
        DatasetVersionVideo,
        DatasetVersionVideoQuery,
        DatasetVersionVideoCreateRequest,
        DatasetVersionVideoCreateRequest,  # no update — immutable join
        BaseEntityDeleteRequest,
    ]
):
    entity_model = DatasetVersionVideoModel
    entity = DatasetVersionVideo
    entity_query = DatasetVersionVideoQuery
    entity_create_request = DatasetVersionVideoCreateRequest
    entity_update_request = DatasetVersionVideoCreateRequest
    entity_delete_request = BaseEntityDeleteRequest

    def _apply_entity_specific_search(
        self, query: DatasetVersionVideoQuery, stmt: Select[tuple[DatasetVersionVideoModel]]
    ) -> Select[tuple[DatasetVersionVideoModel]]:
        if query.dataset_version_id:
            stmt = stmt.filter(DatasetVersionVideoModel.dataset_version_id == query.dataset_version_id)
        return stmt


dataset_store = DatasetStore()
dataset_version_store = DatasetVersionStore()
dataset_version_video_store = DatasetVersionVideoStore()
