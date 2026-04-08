from datetime import datetime, timezone
from typing import cast

from database_manager.blueprints.base_entity import BaseEntityDeleteRequest
from dateutil.rrule import rrulestr
from fastapi import APIRouter

from app.blueprints.todo import Todo, TodoCreateRequest, TodoQuery, TodoUpdateRequest
from app.stores.todo import todo_store
from user_management.api.dependencies import UserDependency

router = APIRouter()


def calculate_next_occurrence(
    recurrence_rule: str,
    recurrence_type: str,
    current_due_at: datetime | None,
    recurrence_start: datetime | None,
    recurrence_end: datetime | None,
) -> datetime | None:
    """Calculate the next occurrence for a recurring todo.

    Args:
        recurrence_rule: RRule format string
        recurrence_type: "fixed_schedule" or "from_completion"
        current_due_at: Current due date (used for fixed_schedule)
        recurrence_start: Start of recurrence window
        recurrence_end: End of recurrence window

    Returns:
        The next occurrence datetime, or None if no more occurrences
    """
    now = datetime.now(timezone.utc)

    # Determine the base time for RRule calculation
    if recurrence_type == "fixed_schedule":
        base_time = current_due_at if current_due_at else now
    else:  # from_completion
        base_time = now

    # Parse the RRule (rrulestr lacks complete type stubs, so we cast)
    rule = rrulestr(recurrence_rule, dtstart=base_time)
    raw_result = rule.after(base_time)  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    if raw_result is None:
        return None

    next_occurrence = cast(datetime, raw_result)

    # Ensure timezone awareness
    if next_occurrence.tzinfo is None:
        next_occurrence = next_occurrence.replace(tzinfo=timezone.utc)

    # Check if within recurrence bounds
    if recurrence_start and next_occurrence < recurrence_start:
        return None
    if recurrence_end and next_occurrence > recurrence_end:
        return None

    return next_occurrence


@router.get("/")
async def get_todos(user: UserDependency):
    return await todo_store.search_entities(TodoQuery(user_id=user.id))


@router.post("/")
async def create_todo(user: UserDependency, request: TodoCreateRequest) -> Todo:
    request.user_id = user.id
    return await todo_store.create_entity(request)


@router.patch("/{todo_id}")
async def update_todo(user: UserDependency, todo_id: int, request: TodoUpdateRequest) -> Todo:
    request.id = todo_id

    # Handle recurrence when completing a recurring todo
    if request.completed is True:
        existing_todo = await todo_store.get_entity_by_id(todo_id)
        if existing_todo and existing_todo.recurrence_rule and existing_todo.recurrence_type:
            next_occurrence = calculate_next_occurrence(
                recurrence_rule=existing_todo.recurrence_rule,
                recurrence_type=existing_todo.recurrence_type,
                current_due_at=existing_todo.due_at,
                recurrence_start=existing_todo.recurrence_start,
                recurrence_end=existing_todo.recurrence_end,
            )

            if next_occurrence:
                # Reset the todo for the next occurrence
                request.completed = False
                request.due_at = next_occurrence
                request.due_notification_sent = False

    return await todo_store.update_entity(request)


@router.delete("/{todo_id}")
async def delete_todo(user: UserDependency, todo_id: int) -> Todo:
    return await todo_store.delete_entity(BaseEntityDeleteRequest(id=todo_id))
