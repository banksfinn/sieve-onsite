from fastapi import APIRouter

from database_manager.blueprints.base_entity import BaseEntityDeleteRequest, BaseEntitySearchResponse
from user_management.api.dependencies import UserDependency

from app.blueprints.delivery import Delivery, DeliveryCreateRequest, DeliveryQuery, DeliveryUpdateRequest
from app.blueprints.delivery_access import DeliveryAccess, DeliveryAccessCreateRequest, DeliveryAccessQuery, DeliveryAccessUpdateRequest
from app.blueprints.delivery_feedback import DeliveryFeedback, DeliveryFeedbackCreateRequest, DeliveryFeedbackQuery
from app.blueprints.clip_feedback import ClipFeedback, ClipFeedbackCreateRequest, ClipFeedbackQuery, ClipFeedbackUpdateRequest
from app.llm.feedback_summarizer import FeedbackSummary, summarize_delivery_feedback
from app.stores.clip_feedback import clip_feedback_store
from app.stores.delivery import delivery_store
from app.stores.delivery_access import delivery_access_store
from app.stores.delivery_feedback import delivery_feedback_store

router = APIRouter()


# --- Delivery CRUD ---


@router.get("", response_model=BaseEntitySearchResponse[Delivery])
async def search_deliveries(user: UserDependency, query: DeliveryQuery = DeliveryQuery()):
    return await delivery_store.search_entities(query)


@router.get("/{delivery_id}", response_model=Delivery)
async def get_delivery(user: UserDependency, delivery_id: int):
    return await delivery_store.get_entity_by_id(delivery_id)


@router.post("", response_model=Delivery)
async def create_delivery(user: UserDependency, request: DeliveryCreateRequest):
    request.created_by = user.id
    return await delivery_store.create_entity(request)


@router.patch("/{delivery_id}", response_model=Delivery)
async def update_delivery(user: UserDependency, delivery_id: int, request: DeliveryUpdateRequest):
    request.id = delivery_id
    return await delivery_store.update_entity(request)


@router.delete("/{delivery_id}", response_model=Delivery)
async def delete_delivery(user: UserDependency, delivery_id: int):
    return await delivery_store.delete_entity(BaseEntityDeleteRequest(id=delivery_id))


# --- Delivery Access ---


@router.get("/{delivery_id}/access", response_model=BaseEntitySearchResponse[DeliveryAccess])
async def search_delivery_access(user: UserDependency, delivery_id: int):
    return await delivery_access_store.search_entities(DeliveryAccessQuery(delivery_id=delivery_id))


@router.post("/{delivery_id}/access", response_model=DeliveryAccess)
async def create_delivery_access(user: UserDependency, delivery_id: int, request: DeliveryAccessCreateRequest):
    request.delivery_id = delivery_id
    return await delivery_access_store.create_entity(request)


@router.patch("/{delivery_id}/access/{access_id}", response_model=DeliveryAccess)
async def update_delivery_access(user: UserDependency, delivery_id: int, access_id: int, request: DeliveryAccessUpdateRequest):
    request.id = access_id
    return await delivery_access_store.update_entity(request)


@router.delete("/{delivery_id}/access/{access_id}", response_model=DeliveryAccess)
async def delete_delivery_access(user: UserDependency, delivery_id: int, access_id: int):
    return await delivery_access_store.delete_entity(BaseEntityDeleteRequest(id=access_id))


# --- Delivery Feedback ---


@router.get("/{delivery_id}/feedback", response_model=BaseEntitySearchResponse[DeliveryFeedback])
async def search_delivery_feedback(user: UserDependency, delivery_id: int):
    return await delivery_feedback_store.search_entities(DeliveryFeedbackQuery(delivery_id=delivery_id))


@router.post("/{delivery_id}/feedback", response_model=DeliveryFeedback)
async def create_delivery_feedback(user: UserDependency, delivery_id: int, request: DeliveryFeedbackCreateRequest):
    request.delivery_id = delivery_id
    request.user_id = user.id
    return await delivery_feedback_store.create_entity(request)


# --- Clip Feedback (scoped to delivery) ---


@router.get("/{delivery_id}/clip/{clip_id}/feedback", response_model=BaseEntitySearchResponse[ClipFeedback])
async def search_clip_feedback(user: UserDependency, delivery_id: int, clip_id: int):
    return await clip_feedback_store.search_entities(ClipFeedbackQuery(delivery_id=delivery_id, clip_id=clip_id))


@router.post("/{delivery_id}/clip/{clip_id}/feedback", response_model=ClipFeedback)
async def create_clip_feedback(user: UserDependency, delivery_id: int, clip_id: int, request: ClipFeedbackCreateRequest):
    request.delivery_id = delivery_id
    request.clip_id = clip_id
    request.user_id = user.id
    return await clip_feedback_store.create_entity(request)


@router.patch("/{delivery_id}/clip/{clip_id}/feedback/{feedback_id}", response_model=ClipFeedback)
async def update_clip_feedback(user: UserDependency, delivery_id: int, clip_id: int, feedback_id: int, request: ClipFeedbackUpdateRequest):
    request.id = feedback_id
    return await clip_feedback_store.update_entity(request)


# --- Feedback Summarization ---


@router.post("/{delivery_id}/summarize-feedback", response_model=FeedbackSummary)
async def summarize_feedback(user: UserDependency, delivery_id: int):
    """Summarize all clip feedback for a delivery using LLM."""
    result = await clip_feedback_store.search_entities(ClipFeedbackQuery(delivery_id=delivery_id, limit=10000))
    return await summarize_delivery_feedback(delivery_id, result.entities)
