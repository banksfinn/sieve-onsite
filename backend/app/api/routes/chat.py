"""Chat API routes for natural language todo management."""

import uuid
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field, SecretStr

from app.llm.prompts.orchestrator import ORCHESTRATOR_SYSTEM_PROMPT
from app.llm.tools.todo_tools import get_todo_tools
from llm_manager.clients.openai_client import OpenAIProvider
from llm_manager.conversation.loop import LLMConversationLoop, LLMLoopConfig
from llm_manager.executor.tool_executor import LLMToolExecutor
from llm_manager.schemas.config import LLMProviderConfig
from llm_manager.schemas.tools import LLMToolContext
from llm_manager.stores.conversation_message import llm_database_store
from user_management.api.dependencies import UserDependency

router = APIRouter()


class ChatRequest(BaseModel):
    """Request to send a chat message."""

    message: str = Field(..., description="The user's message")
    conversation_id: str | None = Field(default=None, description="Conversation ID for continuity")
    timezone: str | None = Field(
        default=None,
        description="User's IANA timezone (e.g., 'America/New_York'). Used for interpreting time references.",
    )


class ChatResponse(BaseModel):
    """Response from the chat endpoint."""

    response: str = Field(..., description="The assistant's response")
    conversation_id: str = Field(..., description="Conversation ID for follow-up messages")


def _create_provider() -> OpenAIProvider:
    """Create an OpenAI provider with settings from environment."""
    from llm_manager.core.settings import llm_settings

    config = LLMProviderConfig(
        api_key=SecretStr(llm_settings.OPENAI_API_KEY),
        model=llm_settings.OPENAI_MODEL,
        base_url=llm_settings.OPENAI_BASE_URL,
    )
    return OpenAIProvider(config)


def _create_executor(provider: OpenAIProvider) -> LLMToolExecutor:
    """Create a tool executor with all todo tools registered.

    Args:
        provider: LLM provider passed to tools that need extraction capabilities
    """
    executor = LLMToolExecutor()
    for tool in get_todo_tools(provider):
        executor.register(tool)
    return executor


@router.post("/", response_model=ChatResponse)
async def chat(user: UserDependency, request: ChatRequest) -> ChatResponse:
    """Send a message to the todo assistant.

    The assistant can help manage todos through natural language:
    - "Show me my todos"
    - "Create a todo to buy groceries due tomorrow"
    - "Mark todo 5 as complete"
    - "What's on my plate for this week?"

    When creating todos, the system automatically extracts:
    - Due dates from phrases like "tomorrow", "next Tuesday"
    - Recurrence patterns from phrases like "every week", "daily"
    - Relevant tags based on the todo content
    """
    provider = _create_provider()
    executor = _create_executor(provider)

    loop = LLMConversationLoop(
        provider=provider,
        executor=executor,
        system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
        config=LLMLoopConfig(max_iterations=10),
    )

    conversation_id = request.conversation_id or str(uuid.uuid4())

    context = LLMToolContext(
        conversation_id=conversation_id,
        user_id=str(user.id),
        metadata={"timezone": request.timezone} if request.timezone else {},
    )

    response_text = await loop.run_with_history(
        user_input=request.message,
        context=context,
        conversation_id=conversation_id,
        store=llm_database_store,
    )

    return ChatResponse(
        response=response_text,
        conversation_id=conversation_id,
    )


class ToolsResponse(BaseModel):
    """Response listing available tools."""

    tools: list[dict[str, Any]]


@router.get("/tools", response_model=ToolsResponse)
async def get_available_tools() -> ToolsResponse:
    """Get list of available tools for the chat assistant."""
    provider = _create_provider()
    executor = _create_executor(provider)
    definitions = executor.get_definitions()
    return ToolsResponse(
        tools=[{"name": d.name, "description": d.description, "parameters": d.parameters} for d in definitions]
    )
