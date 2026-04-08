from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database_manager.blueprints.base_entity import BaseEntityDeleteRequest, BaseEntitySearchResponse
from logging_manager.logger import get_logger
from database_manager.utils.transaction_handler import atomic
from sieve_types.query import SortOrder
from user_management.api.dependencies import UserDependency

from app.blueprints.clip import Clip, ClipCreateRequest, ClipQuery
from app.blueprints.clip_feedback import ClipFeedback, ClipFeedbackCreateRequest, ClipFeedbackQuery, ClipFeedbackUpdateRequest
from app.llm.feedback_summarizer import FeedbackSummary, summarize_dataset_feedback
from app.stores.clip_feedback import clip_feedback_store
from app.blueprints.dataset import (
    Dataset,
    DatasetCreateRequest,
    DatasetQuery,
    DatasetUpdateRequest,
    DatasetVersion,
    DatasetVersionCreateRequest,
    DatasetVersionQuery,
    DatasetVersionVideo,
    DatasetVersionVideoCreateRequest,
    DatasetVersionVideoQuery,
)
from app.blueprints.dataset_assignment import DatasetAssignmentCreateRequest
from app.blueprints.video import Video, VideoCreateRequest, VideoQuery
from app.schemas.enums import DatasetStatus, UserRole
from app.services.gcs_ingest import IngestResult, ParsedClip, ingest_from_gcs
from app.stores.clip import clip_store
from app.stores.dataset import dataset_store, dataset_version_store, dataset_version_video_store
from app.stores.dataset_assignment import dataset_assignment_store
from app.stores.video import video_store

router = APIRouter()
logger = get_logger()


# --- Request/Response models ---


class ClipMetadataEntry(BaseModel):
    video_id: str
    uri: str
    clip_start_time: float
    clip_end_time: float
    clip_duration: float
    extra_metadata: dict | None = None


class DatasetCreateFromBucketRequest(BaseModel):
    name: str
    description: str | None = None
    bucket_path: str | None = None
    clip_metadata: list[ClipMetadataEntry] | None = None


class DatasetCreateResponse(BaseModel):
    dataset: Dataset
    version: DatasetVersion | None = None
    videos_created: int = 0
    clips_created: int = 0


# --- Helpers ---


def _parse_bucket_path(bucket_path: str) -> tuple[str, str]:
    """Parse 'gs://bucket-name/prefix/' into (bucket_name, prefix)."""
    path = bucket_path.removeprefix("gs://")
    parts = path.split("/", 1)
    bucket_name = parts[0]
    prefix = parts[1] if len(parts) > 1 else ""
    return bucket_name, prefix


async def _find_or_create_video(
    delivery_id: str,
    bucket_path: str,
    fps: float | None,
    height: int | None,
    width: int | None,
    extra_metadata: dict | None,
) -> tuple[Video, bool]:
    """Find a video by delivery_id, or create one. Returns (video, was_created)."""
    existing = await video_store.search_entities(VideoQuery(delivery_id=delivery_id, limit=1))
    if existing.entities:
        return existing.entities[0], False

    video = await video_store.create_entity(
        VideoCreateRequest(
            delivery_id=delivery_id,
            uri=f"{bucket_path}/{delivery_id}",
            fps=fps,
            height=height,
            width=width,
            extra_metadata=extra_metadata or None,
        )
    )
    return video, True


async def _create_clips_for_version(
    clips: list[ParsedClip],
    video_id_map: dict[str, int],
    version_id: int,
    bucket_path: str,
) -> int:
    """Create clip records for a version. Returns count created."""
    created = 0
    for clip in clips:
        video_id = video_id_map.get(clip.video_id)
        if video_id is None:
            # Auto-create video from clip reference
            video, _ = await _find_or_create_video(
                delivery_id=clip.video_id,
                bucket_path=bucket_path,
                fps=None,
                height=None,
                width=None,
                extra_metadata=None,
            )
            video_id = video.id
            video_id_map[clip.video_id] = video_id
        await clip_store.create_entity(
            ClipCreateRequest(
                video_id=video_id,
                dataset_version_id=version_id,
                uri=clip.uri,
                start_time=clip.clip_start_time,
                end_time=clip.clip_end_time,
                duration=clip.clip_duration,
                extra_metadata=clip.extra_metadata or None,
            )
        )
        created += 1
    return created


# --- Dataset CRUD ---


@router.get("", response_model=BaseEntitySearchResponse[Dataset])
async def search_datasets(user: UserDependency, query: DatasetQuery = DatasetQuery()):
    return await dataset_store.search_entities(query)


@router.get("/{dataset_id}", response_model=Dataset)
async def get_dataset(user: UserDependency, dataset_id: int):
    return await dataset_store.get_entity_by_id(dataset_id)


@router.post("", response_model=DatasetCreateResponse)
@atomic
async def create_dataset(user: UserDependency, request: DatasetCreateFromBucketRequest):
    """Create a dataset. If bucket_path is provided, ingest metadata from GCS.

    With bucket_path: fetches metadata, creates version 1 (clips),
    sets status to active. Without bucket_path: creates dataset in requested status.

    Only GTM and customer roles can create datasets. Researchers cannot.
    The creator is auto-assigned: GTM as gtm_lead, customer as customer.
    """
    if user.role == UserRole.researcher.value:
        raise HTTPException(status_code=403, detail="Researchers cannot create datasets")

    # Create dataset
    dataset = await dataset_store.create_entity(
        DatasetCreateRequest(
            name=request.name,
            description=request.description,
            bucket_path=request.bucket_path,
        )
    )

    # Auto-assign the creator
    if user.role == UserRole.gtm.value:
        await dataset_assignment_store.create_entity(
            DatasetAssignmentCreateRequest(dataset_id=dataset.id, user_id=user.id, role="gtm_lead")
        )
    elif user.role == UserRole.customer.value:
        await dataset_assignment_store.create_entity(
            DatasetAssignmentCreateRequest(dataset_id=dataset.id, user_id=user.id, role="customer")
        )

    # If no bucket path, just create the dataset in requested status
    if not request.bucket_path:
        logger.info("Dataset created without bucket path", dataset_id=dataset.id, name=request.name)
        return DatasetCreateResponse(dataset=dataset)

    bucket_name, prefix = _parse_bucket_path(request.bucket_path)
    logger.info("Ingesting dataset from GCS", dataset_id=dataset.id, bucket_name=bucket_name, prefix=prefix)

    # Fetch metadata from GCS
    try:
        ingest_result: IngestResult = ingest_from_gcs(bucket_name, prefix)
    except FileNotFoundError as e:
        logger.error("GCS metadata files not found", bucket_name=bucket_name, prefix=prefix, error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("GCS ingest failed", bucket_name=bucket_name, prefix=prefix, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to ingest from GCS: {e}")

    logger.info("GCS metadata loaded", videos=len(ingest_result.videos), clips=len(ingest_result.clips))

    # Find or create videos
    video_id_map: dict[str, int] = {}
    videos_created = 0

    for parsed_video in ingest_result.videos:
        video, was_created = await _find_or_create_video(
            delivery_id=parsed_video.video_id,
            bucket_path=request.bucket_path,
            fps=parsed_video.fps,
            height=parsed_video.height,
            width=parsed_video.width,
            extra_metadata=parsed_video.extra_metadata,
        )
        video_id_map[parsed_video.video_id] = video.id
        if was_created:
            videos_created += 1

    # Determine clips: use provided metadata or all from GCS
    if request.clip_metadata:
        clips_to_create = [
            ParsedClip(
                video_id=c.video_id,
                uri=c.uri,
                clip_start_time=c.clip_start_time,
                clip_end_time=c.clip_end_time,
                clip_duration=c.clip_duration,
                extra_metadata=c.extra_metadata or {},
            )
            for c in request.clip_metadata
        ]
    else:
        clips_to_create = ingest_result.clips

    # Create version 1 (clips)
    version_1 = await dataset_version_store.create_entity(
        DatasetVersionCreateRequest(
            dataset_id=dataset.id,
            version_number=1,
            parent_version_id=None,
            created_by=user.id,
        )
    )

    logger.info("Creating clips for version 1", clip_count=len(clips_to_create), version_id=version_1.id)

    clips_created = await _create_clips_for_version(
        clips_to_create, video_id_map, version_1.id, request.bucket_path
    )

    # Set dataset to active
    dataset = await dataset_store.update_entity(
        DatasetUpdateRequest(
            id=dataset.id,
            status=DatasetStatus.active.value,
        )
    )

    logger.info(
        "Dataset creation complete",
        dataset_id=dataset.id,
        videos_created=videos_created,
        clips_created=clips_created,
    )

    return DatasetCreateResponse(
        dataset=dataset,
        version=version_1,
        videos_created=videos_created,
        clips_created=clips_created,
    )


# --- Ingest (attach bucket to existing dataset) ---


class DatasetIngestRequest(BaseModel):
    bucket_path: str
    clip_metadata: list[ClipMetadataEntry] | None = None


class DatasetIngestResponse(BaseModel):
    dataset: Dataset
    version: DatasetVersion
    videos_created: int
    clips_created: int


@router.post("/{dataset_id}/ingest", response_model=DatasetIngestResponse)
@atomic
async def ingest_dataset(user: UserDependency, dataset_id: int, request: DatasetIngestRequest):
    """Attach a GCS bucket to an existing dataset and ingest its metadata.

    Creates version 0 (source videos) and version 1 (clips), transitions
    the dataset to active status. Intended for GTM/researchers to fulfill
    a customer-requested dataset.
    """
    dataset = await dataset_store.get_entity_by_id(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if dataset.status != DatasetStatus.requested.value:
        raise HTTPException(status_code=409, detail="Dataset is already ingested")

    bucket_name, prefix = _parse_bucket_path(request.bucket_path)
    logger.info("Ingesting into existing dataset", dataset_id=dataset_id, bucket_name=bucket_name, prefix=prefix)

    try:
        ingest_result: IngestResult = ingest_from_gcs(bucket_name, prefix)
    except FileNotFoundError as e:
        logger.error("GCS metadata files not found", dataset_id=dataset_id, bucket_name=bucket_name, prefix=prefix, error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("GCS ingest failed", dataset_id=dataset_id, bucket_name=bucket_name, prefix=prefix, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to ingest from GCS: {e}")

    logger.info("GCS metadata loaded", dataset_id=dataset_id, videos=len(ingest_result.videos), clips=len(ingest_result.clips))

    # Find or create videos
    video_id_map: dict[str, int] = {}
    videos_created = 0

    for parsed_video in ingest_result.videos:
        video, was_created = await _find_or_create_video(
            delivery_id=parsed_video.video_id,
            bucket_path=request.bucket_path,
            fps=parsed_video.fps,
            height=parsed_video.height,
            width=parsed_video.width,
            extra_metadata=parsed_video.extra_metadata,
        )
        video_id_map[parsed_video.video_id] = video.id
        if was_created:
            videos_created += 1

    logger.info("Videos processed", dataset_id=dataset_id, videos_created=videos_created, total_videos=len(video_id_map))

    # Determine clips
    if request.clip_metadata:
        clips_to_create = [
            ParsedClip(
                video_id=c.video_id,
                uri=c.uri,
                clip_start_time=c.clip_start_time,
                clip_end_time=c.clip_end_time,
                clip_duration=c.clip_duration,
                extra_metadata=c.extra_metadata or {},
            )
            for c in request.clip_metadata
        ]
    else:
        clips_to_create = ingest_result.clips

    # Create version 1 (clips)
    version_1 = await dataset_version_store.create_entity(
        DatasetVersionCreateRequest(
            dataset_id=dataset_id,
            version_number=1,
            parent_version_id=None,
            created_by=user.id,
        )
    )

    logger.info("Creating clips for version 1", dataset_id=dataset_id, clip_count=len(clips_to_create))

    clips_created = await _create_clips_for_version(
        clips_to_create, video_id_map, version_1.id, request.bucket_path
    )

    # Transition to active
    dataset = await dataset_store.update_entity(
        DatasetUpdateRequest(
            id=dataset_id,
            status=DatasetStatus.active.value,
            bucket_path=request.bucket_path,
        )
    )

    logger.info(
        "Dataset ingest complete",
        dataset_id=dataset_id,
        videos_created=videos_created,
        clips_created=clips_created,
    )

    return DatasetIngestResponse(
        dataset=dataset,
        version=version_1,
        videos_created=videos_created,
        clips_created=clips_created,
    )


@router.patch("/{dataset_id}", response_model=Dataset)
async def update_dataset(user: UserDependency, dataset_id: int, request: DatasetUpdateRequest):
    request.id = dataset_id
    return await dataset_store.update_entity(request)


@router.delete("/{dataset_id}", response_model=Dataset)
async def delete_dataset(user: UserDependency, dataset_id: int):
    return await dataset_store.delete_entity(BaseEntityDeleteRequest(id=dataset_id))


# --- Dataset Versions (read-only) ---


@router.get("/{dataset_id}/version", response_model=BaseEntitySearchResponse[DatasetVersion])
async def search_dataset_versions(user: UserDependency, dataset_id: int):
    return await dataset_version_store.search_entities(DatasetVersionQuery(dataset_id=dataset_id))


@router.get("/{dataset_id}/version/{version_id}", response_model=DatasetVersion)
async def get_dataset_version(user: UserDependency, dataset_id: int, version_id: int):
    return await dataset_version_store.get_entity_by_id(version_id)


@router.get("/{dataset_id}/version/{version_id}/videos", response_model=BaseEntitySearchResponse[DatasetVersionVideo])
async def get_version_videos(user: UserDependency, dataset_id: int, version_id: int):
    return await dataset_version_video_store.search_entities(
        DatasetVersionVideoQuery(dataset_version_id=version_id)
    )


@router.get("/{dataset_id}/version/{version_id}/clips", response_model=BaseEntitySearchResponse[Clip])
async def get_version_clips(user: UserDependency, dataset_id: int, version_id: int):
    return await clip_store.search_entities(ClipQuery(dataset_version_id=version_id, limit=10000))


class CreateVersionFromClipsRequest(BaseModel):
    clip_ids: list[int]


class CreateVersionFromClipsResponse(BaseModel):
    version: DatasetVersion
    clips_created: int


@router.post("/{dataset_id}/version/{version_id}/fork", response_model=CreateVersionFromClipsResponse)
@atomic
async def fork_version(
    user: UserDependency,
    dataset_id: int,
    version_id: int,
    request: CreateVersionFromClipsRequest,
):
    """Create a new dataset version by selecting a subset of clips from an existing version.

    Copies the selected clips into the new version, simulating a new pipeline run
    where some clips were removed or retained.
    """
    # Verify source version belongs to this dataset
    source_version = await dataset_version_store.get_entity_by_id(version_id)
    if source_version.dataset_id != dataset_id:
        raise HTTPException(status_code=404, detail="Version not found for this dataset")

    # Find latest version number
    existing = await dataset_version_store.search_entities(
        DatasetVersionQuery(dataset_id=dataset_id, limit=1, sort_by="version_number", sort_order=SortOrder.desc)
    )
    next_version_number = (existing.entities[0].version_number + 1) if existing.entities else 1

    # Create new version
    new_version = await dataset_version_store.create_entity(
        DatasetVersionCreateRequest(
            dataset_id=dataset_id,
            version_number=next_version_number,
            parent_version_id=version_id,
            created_by=user.id,
        )
    )

    # Copy selected clips into the new version
    clip_ids_set = set(request.clip_ids)
    source_clips = await clip_store.search_entities(ClipQuery(dataset_version_id=version_id, limit=10000))
    clips_created = 0

    for clip in source_clips.entities:
        if clip.id in clip_ids_set:
            await clip_store.create_entity(
                ClipCreateRequest(
                    video_id=clip.video_id,
                    dataset_version_id=new_version.id,
                    uri=clip.uri,
                    start_time=clip.start_time,
                    end_time=clip.end_time,
                    duration=clip.duration,
                    extra_metadata=clip.extra_metadata,
                )
            )
            clips_created += 1

    return CreateVersionFromClipsResponse(version=new_version, clips_created=clips_created)


# --- Clip Feedback (scoped to dataset version) ---


@router.get("/{dataset_id}/version/{version_id}/clip/{clip_id}/feedback", response_model=BaseEntitySearchResponse[ClipFeedback])
async def search_clip_feedback(user: UserDependency, dataset_id: int, version_id: int, clip_id: int):
    return await clip_feedback_store.search_entities(
        ClipFeedbackQuery(dataset_id=dataset_id, dataset_version_id=version_id, clip_id=clip_id)
    )


@router.post("/{dataset_id}/version/{version_id}/clip/{clip_id}/feedback", response_model=ClipFeedback)
async def create_clip_feedback(user: UserDependency, dataset_id: int, version_id: int, clip_id: int, request: ClipFeedbackCreateRequest):
    request.dataset_id = dataset_id
    request.dataset_version_id = version_id
    request.clip_id = clip_id
    request.user_id = user.id
    return await clip_feedback_store.create_entity(request)


@router.patch("/{dataset_id}/version/{version_id}/clip/{clip_id}/feedback/{feedback_id}", response_model=ClipFeedback)
async def update_clip_feedback(user: UserDependency, dataset_id: int, version_id: int, clip_id: int, feedback_id: int, request: ClipFeedbackUpdateRequest):
    request.id = feedback_id
    return await clip_feedback_store.update_entity(request)


# --- Feedback Summarization ---


@router.post("/{dataset_id}/summarize-feedback", response_model=FeedbackSummary)
async def summarize_feedback(user: UserDependency, dataset_id: int):
    """Summarize all clip feedback for a dataset using LLM."""
    result = await clip_feedback_store.search_entities(ClipFeedbackQuery(dataset_id=dataset_id, limit=10000))
    return await summarize_dataset_feedback(dataset_id, result.entities)
