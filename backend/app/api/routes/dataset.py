from fastapi import APIRouter
from pydantic import BaseModel

from database_manager.blueprints.base_entity import BaseEntityDeleteRequest, BaseEntitySearchResponse
from database_manager.utils.transaction_handler import atomic
from sieve_types.query import SortOrder
from user_management.api.dependencies import UserDependency

from app.blueprints.clip import ClipCreateRequest
from app.blueprints.dataset import (
    Dataset,
    DatasetCreateRequest,
    DatasetQuery,
    DatasetUpdateRequest,
    DatasetVersion,
    DatasetVersionCreateRequest,
    DatasetVersionQuery,
)
from app.blueprints.video import VideoCreateRequest, VideoQuery
from app.stores.clip import clip_store
from app.stores.dataset import dataset_store, dataset_version_store
from app.stores.video import video_store

router = APIRouter()


class ClipMetadataEntry(BaseModel):
    delivery_id: str
    uri: str
    clip_start_time: float
    clip_end_time: float
    clip_duration: float
    avg_face_size: float | None = None
    max_num_faces: int | None = None
    is_full_body: bool | None = None
    has_overlay: bool | None = None


class VideoMetadataEntry(BaseModel):
    delivery_id: str
    fps: float | None = None
    height: int | None = None
    width: int | None = None
    source: str | None = None
    language: str | None = None


class DatasetVersionCreateWithClipsRequest(BaseModel):
    clips: list[ClipMetadataEntry]
    videos: list[VideoMetadataEntry] = []


class DatasetVersionCreateResponse(BaseModel):
    version: DatasetVersion
    clips_created: int
    videos_created: int


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


@router.post("/{dataset_id}/version", response_model=DatasetVersionCreateResponse)
@atomic
async def create_dataset_version(
    user: UserDependency, dataset_id: int, request: DatasetVersionCreateWithClipsRequest
):
    """Create a new dataset version with clip metadata.

    Automatically increments version number. Finds or creates videos by delivery_id,
    then creates clips linked to the new version.
    """
    # Find latest version number for this dataset
    existing_versions = await dataset_version_store.search_entities(
        DatasetVersionQuery(dataset_id=dataset_id, limit=1, sort_by="version_number", sort_order=SortOrder.desc)
    )
    latest_version_number = 0
    parent_version_id = None
    if existing_versions.entities:
        latest_version_number = existing_versions.entities[0].version_number
        parent_version_id = existing_versions.entities[0].id

    # Create new version
    new_version = await dataset_version_store.create_entity(
        DatasetVersionCreateRequest(
            dataset_id=dataset_id,
            version_number=latest_version_number + 1,
            parent_version_id=parent_version_id,
            created_by=user.id,
        )
    )

    # Build a lookup of video metadata by delivery_id
    video_metadata_by_delivery_id: dict[str, VideoMetadataEntry] = {}
    for video_entry in request.videos:
        video_metadata_by_delivery_id[video_entry.delivery_id] = video_entry

    # Find or create videos by delivery_id
    video_id_by_delivery_id: dict[str, int] = {}
    videos_created = 0
    delivery_ids = {clip_entry.delivery_id for clip_entry in request.clips}

    for delivery_id in delivery_ids:
        existing = await video_store.search_entities(VideoQuery(delivery_id=delivery_id, limit=1))
        if existing.entities:
            video_id_by_delivery_id[delivery_id] = existing.entities[0].id
        else:
            meta = video_metadata_by_delivery_id.get(delivery_id)
            video = await video_store.create_entity(
                VideoCreateRequest(
                    delivery_id=delivery_id,
                    uri=f"gs://product-onsite/{delivery_id}",
                    fps=meta.fps if meta else None,
                    height=meta.height if meta else None,
                    width=meta.width if meta else None,
                    source=meta.source if meta else None,
                    language=meta.language if meta else None,
                )
            )
            video_id_by_delivery_id[delivery_id] = video.id
            videos_created += 1

    # Create clips
    clips_created = 0
    for clip_entry in request.clips:
        video_id = video_id_by_delivery_id[clip_entry.delivery_id]
        await clip_store.create_entity(
            ClipCreateRequest(
                video_id=video_id,
                dataset_version_id=new_version.id,
                uri=clip_entry.uri,
                start_time=clip_entry.clip_start_time,
                end_time=clip_entry.clip_end_time,
                duration=clip_entry.clip_duration,
                avg_face_size=clip_entry.avg_face_size,
                max_num_faces=clip_entry.max_num_faces,
                is_full_body=clip_entry.is_full_body,
                has_overlay=clip_entry.has_overlay,
            )
        )
        clips_created += 1

    return DatasetVersionCreateResponse(
        version=new_version,
        clips_created=clips_created,
        videos_created=videos_created,
    )
