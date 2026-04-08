"""Tool registration and execution."""

import asyncio
import json
import traceback
from typing import Any

from pydantic import ValidationError

from llm_manager.core.tool_handler import LLMToolHandler
from llm_manager.schemas.messages import LLMToolCall, LLMToolResult
from llm_manager.schemas.tools import LLMToolContext, LLMToolDefinition


class LLMToolExecutor:
    """Manages tool registration and execution."""

    def __init__(self) -> None:
        self._handlers: dict[str, LLMToolHandler[Any, Any]] = {}

    def register(self, handler: LLMToolHandler[Any, Any]) -> "LLMToolExecutor":
        self._handlers[handler.definition.name] = handler
        return self

    def unregister(self, name: str) -> "LLMToolExecutor":
        self._handlers.pop(name, None)
        return self

    def get_definitions(self) -> list[LLMToolDefinition]:
        return [handler.definition for handler in self._handlers.values()]

    async def execute(self, tool_call: LLMToolCall, context: LLMToolContext) -> LLMToolResult:
        handler = self._handlers.get(tool_call.name)

        if not handler:
            return LLMToolResult(
                tool_call_id=tool_call.id,
                content=f"Error: Unknown tool '{tool_call.name}'",
                is_error=True,
            )

        try:
            input_data: Any = tool_call.arguments
            if handler.input_model:
                try:
                    input_data = handler.input_model.model_validate(tool_call.arguments)
                except ValidationError as e:
                    return LLMToolResult(
                        tool_call_id=tool_call.id,
                        content=f"Validation error: {e}",
                        is_error=True,
                    )

            result = await handler.execute(input_data, context)

            if isinstance(result, str):
                content = result
            elif hasattr(result, "model_dump_json"):
                content = result.model_dump_json()
            else:
                content = json.dumps(result)

            return LLMToolResult(
                tool_call_id=tool_call.id,
                content=content,
                is_error=False,
            )

        except Exception as e:
            return LLMToolResult(
                tool_call_id=tool_call.id,
                content=f"Error executing tool: {e}\n{traceback.format_exc()}",
                is_error=True,
            )

    async def execute_parallel(self, tool_calls: list[LLMToolCall], context: LLMToolContext) -> list[LLMToolResult]:
        tasks = [self.execute(tc, context) for tc in tool_calls]
        return list(await asyncio.gather(*tasks))

    async def execute_sequential(self, tool_calls: list[LLMToolCall], context: LLMToolContext) -> list[LLMToolResult]:
        results: list[LLMToolResult] = []
        for tc in tool_calls:
            result = await self.execute(tc, context)
            results.append(result)
        return results
