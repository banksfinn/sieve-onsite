"""The main conversation orchestration loop."""

from collections.abc import Awaitable, Callable

from pydantic import BaseModel, Field

from llm_manager.clients.provider_base import LLMProvider
from llm_manager.conversation.conversation import LLMConversation, LLMConversationStore
from llm_manager.executor.tool_executor import LLMToolExecutor
from llm_manager.schemas.messages import LLMMessage, LLMToolCall, LLMToolResult
from llm_manager.schemas.tools import LLMToolContext


class LLMMaxIterationsExceeded(Exception):
    def __init__(self, max_iterations: int, last_response: LLMMessage | None = None) -> None:
        self.max_iterations = max_iterations
        self.last_response = last_response
        super().__init__(f"Conversation loop exceeded {max_iterations} iterations")


class LLMLoopConfig(BaseModel):
    max_iterations: int = Field(default=10, ge=1)
    parallel_tool_execution: bool = Field(default=True)


class LLMConversationLoop:
    """Orchestrates the conversation loop with tool execution."""

    def __init__(
        self,
        provider: LLMProvider,
        executor: LLMToolExecutor,
        system_prompt: str | None = None,
        config: LLMLoopConfig | None = None,
    ) -> None:
        self.provider = provider
        self.executor = executor
        self.system_prompt = system_prompt
        self.config = config or LLMLoopConfig()

    async def run(
        self,
        user_input: str,
        context: LLMToolContext,
        conversation: LLMConversation | None = None,
        on_tool_call: Callable[[LLMToolCall], Awaitable[None]] | None = None,
        on_tool_result: Callable[[LLMToolResult], Awaitable[None]] | None = None,
        on_response: Callable[[LLMMessage], Awaitable[None]] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        model: str | None = None,
    ) -> str:
        """Run the conversation loop. Returns the final assistant response content."""
        if conversation is None:
            conversation = LLMConversation()

        user_message = LLMMessage.user(user_input)
        await conversation.append(user_message)

        tools = self.executor.get_definitions()
        last_response: LLMMessage | None = None

        for _ in range(self.config.max_iterations):
            response = await self.provider.chat(
                messages=conversation.messages,
                tools=tools if tools else None,
                system=self.system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                model=model,
            )
            await conversation.append(response)
            last_response = response

            if on_response:
                await on_response(response)

            if not response.tool_calls:
                return response.content or ""

            for tool_call in response.tool_calls:
                if on_tool_call:
                    await on_tool_call(tool_call)

            if self.config.parallel_tool_execution:
                results = await self.executor.execute_parallel(response.tool_calls, context)
            else:
                results = await self.executor.execute_sequential(response.tool_calls, context)

            for result in results:
                if on_tool_result:
                    await on_tool_result(result)

            tool_results_message = LLMMessage.tool_result(results)
            await conversation.append(tool_results_message)

        raise LLMMaxIterationsExceeded(self.config.max_iterations, last_response)

    async def run_with_history(
        self,
        user_input: str,
        context: LLMToolContext,
        conversation_id: str,
        store: LLMConversationStore,
        on_tool_call: Callable[[LLMToolCall], Awaitable[None]] | None = None,
        on_tool_result: Callable[[LLMToolResult], Awaitable[None]] | None = None,
        on_response: Callable[[LLMMessage], Awaitable[None]] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        model: str | None = None,
    ) -> str:
        """Run the conversation loop with persistent history."""
        conversation = LLMConversation(id=conversation_id, store=store)
        await conversation.load()

        return await self.run(
            user_input=user_input,
            context=context,
            conversation=conversation,
            on_tool_call=on_tool_call,
            on_tool_result=on_tool_result,
            on_response=on_response,
            temperature=temperature,
            max_tokens=max_tokens,
            model=model,
        )
