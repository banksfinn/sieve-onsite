from fastapi import APIRouter
from pydantic import BaseModel

from database_manager.blueprints.base_entity import BaseEntitySearchResponse
from user_management.api.dependencies import UserDependency

from app.blueprints.clip import ClipQuery
from app.blueprints.dataset_review import (
    DatasetReview,
    DatasetReviewCreateRequest,
    DatasetReviewQuery,
    DatasetReviewReply,
    DatasetReviewReplyCreateRequest,
    DatasetReviewReplyQuery,
    DatasetReviewUpdateRequest,
)
from app.schemas.enums import ReviewStatus, ReviewType
from app.stores.clip import clip_store
from app.stores.dataset_review import dataset_review_store, dataset_review_reply_store

router = APIRouter()


# --- Reviews ---


@router.get("/{dataset_id}/review", response_model=BaseEntitySearchResponse[DatasetReview])
async def search_reviews(
    user: UserDependency,
    dataset_id: int,
    dataset_version_id: int | None = None,
    clip_id: int | None = None,
    status: ReviewStatus | None = None,
    review_type: ReviewType | None = None,
):
    return await dataset_review_store.search_entities(
        DatasetReviewQuery(
            dataset_id=dataset_id,
            dataset_version_id=dataset_version_id,
            clip_id=clip_id,
            status=status,
            review_type=review_type,
            limit=10000,
        )
    )


@router.post("/{dataset_id}/version/{version_id}/review", response_model=DatasetReview)
async def create_review(
    user: UserDependency,
    dataset_id: int,
    version_id: int,
    request: DatasetReviewCreateRequest,
):
    request.dataset_id = dataset_id
    request.dataset_version_id = version_id
    request.user_id = user.id
    return await dataset_review_store.create_entity(request)


@router.patch("/{dataset_id}/review/{review_id}", response_model=DatasetReview)
async def update_review(
    user: UserDependency,
    dataset_id: int,
    review_id: int,
    request: DatasetReviewUpdateRequest,
):
    request.id = review_id
    return await dataset_review_store.update_entity(request)


# --- Review Replies ---


@router.get("/{dataset_id}/review/{review_id}/reply", response_model=BaseEntitySearchResponse[DatasetReviewReply])
async def search_replies(
    user: UserDependency,
    dataset_id: int,
    review_id: int,
):
    return await dataset_review_reply_store.search_entities(
        DatasetReviewReplyQuery(review_id=review_id, limit=10000)
    )


@router.post("/{dataset_id}/review/{review_id}/reply", response_model=DatasetReviewReply)
async def create_reply(
    user: UserDependency,
    dataset_id: int,
    review_id: int,
    request: DatasetReviewReplyCreateRequest,
):
    request.review_id = review_id
    request.user_id = user.id
    return await dataset_review_reply_store.create_entity(request)


# --- Active Comments (for researcher post-version-creation flow) ---


class ActiveComment(BaseModel):
    review: DatasetReview
    replies: list[DatasetReviewReply]
    clip_removed: bool = False
    auto_completed: bool = False


class ActiveCommentsResponse(BaseModel):
    top_level: list[ActiveComment]
    by_clip: dict[str, list[ActiveComment]]
    auto_completed_count: int


@router.get(
    "/{dataset_id}/version/{version_id}/active-comments",
    response_model=ActiveCommentsResponse,
)
async def get_active_comments(
    user: UserDependency,
    dataset_id: int,
    version_id: int,
):
    """Get open reviews from prior versions, with auto-completion detection.

    For each open review:
    - If it references a clip not in this version and is a deletion request → auto_completed
    - If it references a clip not in this version but is a review → elevated to top-level, clip_removed=True
    """
    # Get all open reviews for this dataset
    open_reviews = await dataset_review_store.search_entities(
        DatasetReviewQuery(dataset_id=dataset_id, status=ReviewStatus.open, limit=10000)
    )

    # Get clip IDs in the current version
    version_clips = await clip_store.search_entities(
        ClipQuery(dataset_version_id=version_id, limit=10000)
    )
    current_clip_ids = {c.id for c in version_clips.entities}

    top_level: list[ActiveComment] = []
    by_clip: dict[str, list[ActiveComment]] = {}
    auto_completed_count = 0

    for review in open_reviews.entities:
        # Don't show reviews from this version itself
        if review.dataset_version_id == version_id:
            continue

        # Fetch replies for this review
        replies_response = await dataset_review_reply_store.search_entities(
            DatasetReviewReplyQuery(review_id=review.id, limit=10000)
        )
        replies = replies_response.entities

        clip_removed = False
        auto_completed = False

        if review.clip_id is not None and review.clip_id not in current_clip_ids:
            clip_removed = True
            if review.review_type == ReviewType.request_for_deletion:
                auto_completed = True
                auto_completed_count += 1

        comment = ActiveComment(
            review=review,
            replies=replies,
            clip_removed=clip_removed,
            auto_completed=auto_completed,
        )

        # Top-level if no clip, or clip was removed
        if review.clip_id is None or clip_removed:
            top_level.append(comment)
        else:
            clip_key = str(review.clip_id)
            if clip_key not in by_clip:
                by_clip[clip_key] = []
            by_clip[clip_key].append(comment)

    return ActiveCommentsResponse(
        top_level=top_level,
        by_clip=by_clip,
        auto_completed_count=auto_completed_count,
    )
