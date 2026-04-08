"""LLM tools for todo management.

These tools are exposed to the orchestrator LLM for managing todos.
The create_todo tool internally uses extractors to parse dates, recurrence, and tags.
"""

from datetime import datetime, timezone
from typing import Any, cast

from database_manager.blueprints.base_entity import BaseEntityDeleteRequest
from dateutil.rrule import rrulestr
from llm_manager.clients.provider_base import LLMProvider
from llm_manager.core.tool_handler import LLMToolHandler
from llm_manager.schemas.tools import LLMToolContext, LLMToolDefinition
from pydantic import BaseModel, Field

from app.blueprints.tag import TagQuery
from app.blueprints.todo import Todo, TodoCreateRequest, TodoQuery, TodoUpdateRequest
from app.llm.extractors.due_date import extract_due_date
from app.llm.extractors.recurrence import extract_recurrence
from app.llm.extractors.tags import extract_tags
from app.stores.tag import tag_store
from app.stores.todo import todo_store


def _todo_to_dict(todo: Todo) -> dict[str, Any]:
    """Convert a todo to a dict for LLM consumption."""
    return {
        "id": todo.id,
        "title": todo.title,
        "description": todo.description,
        "completed": todo.completed,
        "due_at": todo.due_at.isoformat() if todo.due_at else None,
        "recurrence_rule": todo.recurrence_rule,
        "recurrence_type": todo.recurrence_type,
        "tags": [{"id": t.id, "name": t.name, "icon": t.icon} for t in todo.tags],
        "slack_notification": todo.slack_notification,
        "notification_timing_override": todo.notification_timing_override,
    }


# --- List Todos Tool ---


class ListTodosInput(BaseModel):
    """Input for listing todos."""

    completed: bool | None = Field(default=None, description="Filter by completion status")
    due_before: str | None = Field(default=None, description="Filter to todos due before this ISO date")


class ListTodosTool(LLMToolHandler[ListTodosInput, list[dict[str, Any]]]):
    """List all todos for the current user."""

    @property
    def definition(self) -> LLMToolDefinition:
        return LLMToolDefinition(
            name="list_todos",
            description="List all todos for the current user. Can filter by completion status or due date.",
            parameters={
                "type": "object",
                "properties": {
                    "completed": {
                        "type": "boolean",
                        "description": "Filter by completion status (true=completed, false=incomplete)",
                    },
                    "due_before": {
                        "type": "string",
                        "description": "Filter to todos due before this ISO date (e.g. 2024-01-15T00:00:00Z)",
                    },
                },
                "required": [],
            },
        )

    @property
    def input_model(self) -> type[ListTodosInput]:
        return ListTodosInput

    async def execute(self, input: ListTodosInput | dict[str, Any], context: LLMToolContext) -> list[dict[str, Any]]:
        if isinstance(input, dict):
            input = ListTodosInput.model_validate(input)

        user_id = int(context.user_id) if context.user_id else None
        if not user_id:
            return [{"error": "No user context available"}]

        query = TodoQuery(user_id=user_id, completed=input.completed)

        if input.due_before:
            query.due_before = datetime.fromisoformat(input.due_before.replace("Z", "+00:00"))

        result = await todo_store.search_entities(query)
        return [_todo_to_dict(t) for t in result.entities]


# --- Search Todos Tool ---


class SearchTodosInput(BaseModel):
    """Input for searching todos."""

    query: str = Field(..., description="Search query to match against todo titles")


class SearchTodosTool(LLMToolHandler[SearchTodosInput, list[dict[str, Any]]]):
    """Search todos by title."""

    @property
    def definition(self) -> LLMToolDefinition:
        return LLMToolDefinition(
            name="search_todos",
            description="Search for todos by title. Returns todos where the title contains the search query.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Text to search for in todo titles",
                    },
                },
                "required": ["query"],
            },
        )

    @property
    def input_model(self) -> type[SearchTodosInput]:
        return SearchTodosInput

    async def execute(self, input: SearchTodosInput | dict[str, Any], context: LLMToolContext) -> list[dict[str, Any]]:
        if isinstance(input, dict):
            input = SearchTodosInput.model_validate(input)

        user_id = int(context.user_id) if context.user_id else None
        if not user_id:
            return [{"error": "No user context available"}]

        result = await todo_store.search_entities(TodoQuery(user_id=user_id))
        query_lower = input.query.lower()
        matching = [t for t in result.entities if query_lower in t.title.lower()]
        return [_todo_to_dict(t) for t in matching]


# --- Create Todo Tool (with extraction) ---


class CreateTodoInput(BaseModel):
    """Input for creating a todo."""

    description: str = Field(..., description="Natural language description of the todo, including any dates or recurrence")
    title: str | None = Field(
        default=None,
        description="Clean, concise title for the todo (without temporal info or tag references). If not provided, uses description.",
    )
    slack_notification: bool = Field(
        default=False, description="Whether to send Slack notification before due date (requires due date)"
    )
    notification_timing_override: list[str] | None = Field(
        default=None,
        description="Custom notification timing(s). Options: '30_minutes_before', '1_hour_before', '2_hours_before', '1_day_before', '1_week_before'. If None, uses user's default timing.",
    )


class CreateTodoTool(LLMToolHandler[CreateTodoInput, dict[str, Any]]):
    """Create a new todo from natural language description.

    This tool automatically extracts:
    - Due dates and start dates from the description
    - Recurrence patterns (daily, weekly, etc.)
    - Relevant tags based on the content
    """

    def __init__(self, provider: LLMProvider):
        """Initialize with an LLM provider for extraction calls."""
        self._provider = provider

    @property
    def definition(self) -> LLMToolDefinition:
        return LLMToolDefinition(
            name="create_todo",
            description=(
                "Create a new todo from a natural language description. "
                "The system will automatically extract due dates, recurrence patterns, and relevant tags. "
                "Example: 'buy milk every Tuesday starting next week' will create a recurring todo. "
                "Optionally enable Slack notifications to remind the user before the due date."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Natural language description of the todo (e.g., 'buy groceries tomorrow', 'exercise every weekday')",
                    },
                    "title": {
                        "type": "string",
                        "description": (
                            "Clean, concise title for the todo WITHOUT temporal info (dates, times, recurrence) "
                            "or tag references. E.g., for 'take out the trash at Waller every Sunday at 8pm' "
                            "where 'Waller' is a tag, the title should be 'take out the trash'. "
                            "If not provided, the full description is used as the title."
                        ),
                    },
                    "slack_notification": {
                        "type": "boolean",
                        "description": "Whether to send Slack notification before due date. Defaults to false. Only works if todo has a due date.",
                    },
                    "notification_timing_override": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Custom notification timing(s). Options: '30_minutes_before', '1_hour_before', '2_hours_before', '1_day_before', '1_week_before'. If not provided, uses user's default timing preferences.",
                    },
                },
                "required": ["description"],
            },
        )

    @property
    def input_model(self) -> type[CreateTodoInput]:
        return CreateTodoInput

    async def execute(self, input: CreateTodoInput | dict[str, Any], context: LLMToolContext) -> dict[str, Any]:
        if isinstance(input, dict):
            input = CreateTodoInput.model_validate(input)

        user_id = int(context.user_id) if context.user_id else None
        if not user_id:
            return {"error": "No user context available"}

        current_time = datetime.now(timezone.utc)
        user_timezone = context.metadata.get("timezone") if context.metadata else None

        # Step 1: Extract due dates
        date_result = await extract_due_date(self._provider, input.description, current_time, user_timezone=user_timezone)

        # Step 2: Extract recurrence if signals were found
        recurrence_result = None
        if date_result.has_recurrence_signal:
            recurrence_result = await extract_recurrence(
                self._provider,
                input.description,
                date_result.time_expressions,
                current_time,
            )

        # Step 3: Extract tags
        tag_result = await tag_store.search_entities(TagQuery(user_id=user_id))
        available_tags = [t.name for t in tag_result.entities]
        tag_extraction = await extract_tags(self._provider, input.description, available_tags)

        # Map tag names to IDs
        tag_map: dict[str, int] = {t.name.lower(): t.id for t in tag_result.entities}
        tag_ids = [tag_map[name.lower()] for name in tag_extraction.tag_names if name.lower() in tag_map]

        # Build the create request
        # Use clean title if provided, otherwise fall back to description
        todo_title = input.title if input.title else input.description

        # Only enable slack notification if there's a due date
        enable_slack = input.slack_notification and date_result.due_date is not None
        request = TodoCreateRequest(
            user_id=user_id,
            title=todo_title,
            description=input.description,
            due_at=date_result.due_date,
            recurrence_rule=recurrence_result.recurrence_rule if recurrence_result else None,
            recurrence_type=recurrence_result.recurrence_type if recurrence_result else None,
            recurrence_start=recurrence_result.recurrence_start if recurrence_result else None,
            recurrence_end=recurrence_result.recurrence_end if recurrence_result else None,
            tag_ids=tag_ids,
            slack_notification=enable_slack,
            notification_timing_override=input.notification_timing_override if enable_slack else None,
        )

        todo = await todo_store.create_entity(request)

        # Build extraction summary for response
        extraction_summary = {
            "extracted_due_date": date_result.due_date.isoformat() if date_result.due_date else None,
            "extracted_recurrence": recurrence_result.recurrence_rule if recurrence_result else None,
            "extracted_tags": tag_extraction.tag_names,
        }

        return {
            "success": True,
            "todo": _todo_to_dict(todo),
            "extraction": extraction_summary,
        }


# --- Update Todo Tool ---


class UpdateTodoInput(BaseModel):
    """Input for updating a todo."""

    todo_id: int = Field(..., description="ID of the todo to update")
    title: str | None = Field(default=None, description="New title")
    completed: bool | None = Field(default=None, description="New completion status")
    slack_notification: bool | None = Field(default=None, description="Whether to send Slack notification")
    notification_timing_override: list[str] | None = Field(
        default=None,
        description="Custom notification timing(s). Options: '30_minutes_before', '1_hour_before', '2_hours_before', '1_day_before', '1_week_before'. Set to empty list to use user's defaults.",
    )


class UpdateTodoTool(LLMToolHandler[UpdateTodoInput, dict[str, Any]]):
    """Update an existing todo's title, completion status, or notification settings."""

    @property
    def definition(self) -> LLMToolDefinition:
        return LLMToolDefinition(
            name="update_todo",
            description="Update an existing todo's title, completion status, or Slack notification settings.",
            parameters={
                "type": "object",
                "properties": {
                    "todo_id": {
                        "type": "integer",
                        "description": "ID of the todo to update",
                    },
                    "title": {
                        "type": "string",
                        "description": "New title for the todo",
                    },
                    "completed": {
                        "type": "boolean",
                        "description": "New completion status",
                    },
                    "slack_notification": {
                        "type": "boolean",
                        "description": "Whether to send Slack notification before due date",
                    },
                    "notification_timing_override": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Custom notification timing(s). Options: '30_minutes_before', '1_hour_before', '2_hours_before', '1_day_before', '1_week_before'. Set to empty array to use user's default timing.",
                    },
                },
                "required": ["todo_id"],
            },
        )

    @property
    def input_model(self) -> type[UpdateTodoInput]:
        return UpdateTodoInput

    async def execute(self, input: UpdateTodoInput | dict[str, Any], context: LLMToolContext) -> dict[str, Any]:
        if isinstance(input, dict):
            input = UpdateTodoInput.model_validate(input)

        existing = await todo_store.get_entity_by_id(input.todo_id)
        if not existing:
            return {"error": f"Todo {input.todo_id} not found"}

        # Handle notification_timing_override: empty list means use defaults (None in DB)
        timing_override = input.notification_timing_override
        if timing_override is not None and len(timing_override) == 0:
            timing_override = None

        request = TodoUpdateRequest(
            id=input.todo_id,
            title=input.title,
            completed=input.completed,
            slack_notification=input.slack_notification,
            notification_timing_override=timing_override,
        )

        updated = await todo_store.update_entity(request)
        return {"success": True, "todo": _todo_to_dict(updated)}


# --- Complete Todo Tool ---


class CompleteTodoInput(BaseModel):
    """Input for completing a todo."""

    todo_id: int = Field(..., description="ID of the todo to complete")


class CompleteTodoTool(LLMToolHandler[CompleteTodoInput, dict[str, Any]]):
    """Mark a todo as complete."""

    @property
    def definition(self) -> LLMToolDefinition:
        return LLMToolDefinition(
            name="complete_todo",
            description="Mark a todo as complete. For recurring todos, this advances to the next occurrence.",
            parameters={
                "type": "object",
                "properties": {
                    "todo_id": {
                        "type": "integer",
                        "description": "ID of the todo to complete",
                    },
                },
                "required": ["todo_id"],
            },
        )

    @property
    def input_model(self) -> type[CompleteTodoInput]:
        return CompleteTodoInput

    async def execute(self, input: CompleteTodoInput | dict[str, Any], context: LLMToolContext) -> dict[str, Any]:
        if isinstance(input, dict):
            input = CompleteTodoInput.model_validate(input)

        existing = await todo_store.get_entity_by_id(input.todo_id)
        if not existing:
            return {"error": f"Todo {input.todo_id} not found"}

        request = TodoUpdateRequest(id=input.todo_id, completed=True)

        # Handle recurrence
        if existing.recurrence_rule and existing.recurrence_type:
            next_occurrence = _calculate_next_occurrence(
                recurrence_rule=existing.recurrence_rule,
                recurrence_type=existing.recurrence_type,
                current_due_at=existing.due_at,
                recurrence_start=existing.recurrence_start,
                recurrence_end=existing.recurrence_end,
            )

            if next_occurrence:
                request.completed = False
                request.due_at = next_occurrence
                request.due_notification_sent = False

        updated = await todo_store.update_entity(request)
        return {"success": True, "todo": _todo_to_dict(updated), "was_recurring": existing.recurrence_rule is not None}


# --- Skip Todo Tool ---


class SkipTodoInput(BaseModel):
    """Input for skipping a recurring todo occurrence."""

    todo_id: int = Field(..., description="ID of the recurring todo to skip")


class SkipTodoTool(LLMToolHandler[SkipTodoInput, dict[str, Any]]):
    """Skip the current occurrence of a recurring todo."""

    @property
    def definition(self) -> LLMToolDefinition:
        return LLMToolDefinition(
            name="skip_todo",
            description="Skip the current occurrence of a recurring todo and advance to the next one.",
            parameters={
                "type": "object",
                "properties": {
                    "todo_id": {
                        "type": "integer",
                        "description": "ID of the recurring todo to skip",
                    },
                },
                "required": ["todo_id"],
            },
        )

    @property
    def input_model(self) -> type[SkipTodoInput]:
        return SkipTodoInput

    async def execute(self, input: SkipTodoInput | dict[str, Any], context: LLMToolContext) -> dict[str, Any]:
        if isinstance(input, dict):
            input = SkipTodoInput.model_validate(input)

        existing = await todo_store.get_entity_by_id(input.todo_id)
        if not existing:
            return {"error": f"Todo {input.todo_id} not found"}

        if not existing.recurrence_rule:
            return {"error": "Cannot skip a non-recurring todo"}

        next_occurrence = _calculate_next_occurrence(
            recurrence_rule=existing.recurrence_rule,
            recurrence_type="fixed_schedule",
            current_due_at=existing.due_at,
            recurrence_start=existing.recurrence_start,
            recurrence_end=existing.recurrence_end,
        )

        if not next_occurrence:
            return {"error": "No more occurrences for this recurring todo"}

        request = TodoUpdateRequest(
            id=input.todo_id,
            due_at=next_occurrence,
            due_notification_sent=False,
        )

        updated = await todo_store.update_entity(request)
        return {"success": True, "todo": _todo_to_dict(updated), "skipped_to": next_occurrence.isoformat()}


# --- Delete Todo Tool ---


class DeleteTodoInput(BaseModel):
    """Input for deleting a todo."""

    todo_id: int = Field(..., description="ID of the todo to delete")


class DeleteTodoTool(LLMToolHandler[DeleteTodoInput, dict[str, Any]]):
    """Delete a todo permanently."""

    @property
    def definition(self) -> LLMToolDefinition:
        return LLMToolDefinition(
            name="delete_todo",
            description="Permanently delete a todo. This cannot be undone.",
            parameters={
                "type": "object",
                "properties": {
                    "todo_id": {
                        "type": "integer",
                        "description": "ID of the todo to delete",
                    },
                },
                "required": ["todo_id"],
            },
        )

    @property
    def input_model(self) -> type[DeleteTodoInput]:
        return DeleteTodoInput

    async def execute(self, input: DeleteTodoInput | dict[str, Any], context: LLMToolContext) -> dict[str, Any]:
        if isinstance(input, dict):
            input = DeleteTodoInput.model_validate(input)

        existing = await todo_store.get_entity_by_id(input.todo_id)
        if not existing:
            return {"error": f"Todo {input.todo_id} not found"}

        deleted = await todo_store.delete_entity(BaseEntityDeleteRequest(id=input.todo_id))
        return {"success": True, "deleted_todo": _todo_to_dict(deleted)}


# --- Get Tags Tool ---


class GetTagsInput(BaseModel):
    """Input for getting available tags."""

    pass


class GetTagsTool(LLMToolHandler[GetTagsInput, list[dict[str, Any]]]):
    """Get all tags available to the current user."""

    @property
    def definition(self) -> LLMToolDefinition:
        return LLMToolDefinition(
            name="get_tags",
            description="Get all tags available to the current user.",
            parameters={
                "type": "object",
                "properties": {},
                "required": [],
            },
        )

    @property
    def input_model(self) -> type[GetTagsInput]:
        return GetTagsInput

    async def execute(self, input: GetTagsInput | dict[str, Any], context: LLMToolContext) -> list[dict[str, Any]]:
        user_id = int(context.user_id) if context.user_id else None
        if not user_id:
            return [{"error": "No user context available"}]

        result = await tag_store.search_entities(TagQuery(user_id=user_id))
        return [{"id": t.id, "name": t.name, "icon": t.icon} for t in result.entities]


# --- Helper Functions ---


def _calculate_next_occurrence(
    recurrence_rule: str,
    recurrence_type: str,
    current_due_at: datetime | None,
    recurrence_start: datetime | None,
    recurrence_end: datetime | None,
) -> datetime | None:
    """Calculate the next occurrence for a recurring todo."""
    now = datetime.now(timezone.utc)

    if recurrence_type == "fixed_schedule":
        base_time = current_due_at if current_due_at else now
    else:
        base_time = now

    rule = rrulestr(recurrence_rule, dtstart=base_time)
    raw_result = rule.after(base_time)  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    if raw_result is None:
        return None

    next_occurrence = cast(datetime, raw_result)

    if next_occurrence.tzinfo is None:
        next_occurrence = next_occurrence.replace(tzinfo=timezone.utc)

    if recurrence_start and next_occurrence < recurrence_start:
        return None
    if recurrence_end and next_occurrence > recurrence_end:
        return None

    return next_occurrence


# --- Tool Registration ---


def get_todo_tools(provider: LLMProvider) -> list[LLMToolHandler[Any, Any]]:
    """Get all todo-related LLM tools.

    Args:
        provider: LLM provider for extraction calls (used by create_todo)
    """
    return [
        ListTodosTool(),
        SearchTodosTool(),
        CreateTodoTool(provider),
        UpdateTodoTool(),
        CompleteTodoTool(),
        SkipTodoTool(),
        DeleteTodoTool(),
        GetTagsTool(),
    ]
