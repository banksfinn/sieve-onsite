from fastapi import APIRouter

from database_manager.blueprints.base_entity import BaseEntityDeleteRequest, BaseEntitySearchResponse
from user_management.api.dependencies import UserDependency

from app.blueprints.dataset import (
    Dataset,
    DatasetCreateRequest,
    DatasetQuery,
    DatasetUpdateRequest,
    DatasetVersion,
    DatasetVersionCreateRequest,
    DatasetVersionQuery,
)
from app.stores.dataset import dataset_store, dataset_version_store

router = APIRouter()


# --- Dataset ---


@router.get("", response_model=BaseEntitySearchResponse[Dataset])
async def search_datasets(user: UserDependency, query: DatasetQuery = DatasetQuery()):
    return await dataset_store.search_entities(query)


@router.get("/{dataset_id}", response_model=Dataset)
async def get_dataset(user: UserDependency, dataset_id: int):
    return await dataset_store.get_entity_by_id(dataset_id)


@router.post("", response_model=Dataset)
async def create_dataset(user: UserDependency, request: DatasetCreateRequest):
    return await dataset_store.create_entity(request)


@router.patch("/{dataset_id}", response_model=Dataset)
async def update_dataset(user: UserDependency, dataset_id: int, request: DatasetUpdateRequest):
    request.id = dataset_id
    return await dataset_store.update_entity(request)


@router.delete("/{dataset_id}", response_model=Dataset)
async def delete_dataset(user: UserDependency, dataset_id: int):
    return await dataset_store.delete_entity(BaseEntityDeleteRequest(id=dataset_id))


# --- DatasetVersion ---


@router.get("/{dataset_id}/version", response_model=BaseEntitySearchResponse[DatasetVersion])
async def search_dataset_versions(user: UserDependency, dataset_id: int):
    return await dataset_version_store.search_entities(DatasetVersionQuery(dataset_id=dataset_id))


@router.get("/{dataset_id}/version/{version_id}", response_model=DatasetVersion)
async def get_dataset_version(user: UserDependency, dataset_id: int, version_id: int):
    return await dataset_version_store.get_entity_by_id(version_id)


@router.post("/{dataset_id}/version", response_model=DatasetVersion)
async def create_dataset_version(user: UserDependency, dataset_id: int, request: DatasetVersionCreateRequest):
    request.dataset_id = dataset_id
    request.created_by = user.id
    return await dataset_version_store.create_entity(request)
