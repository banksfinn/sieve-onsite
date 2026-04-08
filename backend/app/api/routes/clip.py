import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database_manager.blueprints.base_entity import BaseEntitySearchResponse
from user_management.api.dependencies import UserDependency

from app.blueprints.clip import Clip, ClipCreateRequest, ClipQuery
from app.stores.clip import clip_store
from storage_manager.clients.gcs_client import GCSClient

router = APIRouter()

# In-memory signed URL cache: gs_uri -> (signed_url, expires_at)
_signed_url_cache: dict[str, tuple[str, float]] = {}
_SIGNED_URL_TTL_MINUTES = 55  # refresh 5 min before the 60-min expiry


def _get_signed_url(gs_uri: str) -> str:
    """Get a signed URL for a gs:// URI, using cache when possible."""
    now = time.time()

    cached = _signed_url_cache.get(gs_uri)
    if cached and cached[1] > now:
        return cached[0]

    if not gs_uri.startswith("gs://"):
        return gs_uri

    path = gs_uri.removeprefix("gs://")
    parts = path.split("/", 1)
    bucket_name = parts[0]
    blob_path = parts[1] if len(parts) > 1 else ""

    gcs = GCSClient(bucket_name=bucket_name)
    signed_url = gcs.generate_signed_url(blob_path, expiration_minutes=60)

    _signed_url_cache[gs_uri] = (signed_url, now + _SIGNED_URL_TTL_MINUTES * 60)
    return signed_url


@router.get("", response_model=BaseEntitySearchResponse[Clip])
async def search_clips(
    user: UserDependency,
    video_id: int | None = None,
    dataset_version_id: int | None = None,
):
    query = ClipQuery(video_id=video_id, dataset_version_id=dataset_version_id)
    return await clip_store.search_entities(query)


@router.get("/{clip_id}", response_model=Clip)
async def get_clip(user: UserDependency, clip_id: int):
    return await clip_store.get_entity_by_id(clip_id)


@router.post("", response_model=Clip)
async def create_clip(user: UserDependency, request: ClipCreateRequest):
    return await clip_store.create_entity(request)


# --- Signed URLs ---


class SignedUrlResponse(BaseModel):
    signed_url: str


@router.get("/{clip_id}/signed-url", response_model=SignedUrlResponse)
async def get_clip_signed_url(user: UserDependency, clip_id: int):
    """Generate a signed URL for a clip's video file (cached for ~55 min)."""
    clip = await clip_store.get_entity_by_id(clip_id)
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    return SignedUrlResponse(signed_url=_get_signed_url(clip.uri))


class BatchSignedUrlRequest(BaseModel):
    clip_ids: list[int]


class BatchSignedUrlResponse(BaseModel):
    urls: dict[str, str]  # clip_id (as string) -> signed_url


@router.post("/batch-signed-urls", response_model=BatchSignedUrlResponse)
async def batch_signed_urls(user: UserDependency, request: BatchSignedUrlRequest):
    """Generate signed URLs for multiple clips in one request.

    Returns a map of clip_id -> signed_url. Uses an in-memory cache
    so repeated URIs (same video across versions) only hit GCS once.
    """
    clip_ids = request.clip_ids[:10000]  # safety cap

    # Fetch all clips in one query
    clips = []
    for cid in clip_ids:
        clip = await clip_store.get_entity_by_id(cid)
        if clip:
            clips.append(clip)

    urls: dict[str, str] = {}
    for clip in clips:
        urls[str(clip.id)] = _get_signed_url(clip.uri)

    return BatchSignedUrlResponse(urls=urls)
