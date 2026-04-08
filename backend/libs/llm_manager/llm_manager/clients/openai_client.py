"""OpenAI provider implementation using the official SDK."""

import json
from collections.abc import AsyncIterator
from typing import Any, cast

import httpx
from openai import AsyncOpenAI

from llm_manager.clients.provider_base import LLMProvider
from llm_manager.schemas.config import LLMProviderConfig
from llm_manager.schemas.messages import LLMMessage, LLMToolCall
from llm_manager.schemas.provider import (
    ProviderChatRequest,
    ProviderChatResponse,
    ProviderMessage,
    ProviderTool,
    ProviderToolCall,
    ProviderToolCallFunction,
    ProviderToolFunction,
)
from llm_manager.schemas.tools import LLMToolDefinition


class OpenAIProvider(LLMProvider):
    """OpenAI provider using the official SDK."""

    def __init__(self, config: LLMProviderConfig):
        super().__init__(config)
        timeout = httpx.Timeout(
            connect=config.timeout.connect_timeout,
            read=config.timeout.read_timeout,
            write=config.timeout.read_timeout,
            pool=config.timeout.connect_timeout,
        )
        self.client = AsyncOpenAI(
            api_key=config.api_key.get_secret_value(),
            base_url=config.base_url,
            timeout=timeout,
            max_retries=config.retry.max_retries,
        )

    async def chat(
        self,
        messages: list[LLMMessage],
        tools: list[LLMToolDefinition] | None = None,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        model: str | None = None,
    ) -> LLMMessage:
        request = self.build_request(
            messages=messages,
            tools=tools,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
            model=model,
            stream=False,
        )

        openai_messages = self._to_openai_messages(request.messages)
        kwargs: dict[str, Any] = {
            "model": request.model,
            "messages": openai_messages,
        }

        if request.tools:
            kwargs["tools"] = self._to_openai_tools(request.tools)
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens

        response = await self.client.chat.completions.create(**kwargs)  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        provider_response = self._from_openai_response(response)
        return self.parse_response(provider_response)

    async def chat_stream(
        self,
        messages: list[LLMMessage],
        tools: list[LLMToolDefinition] | None = None,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        model: str | None = None,
    ) -> AsyncIterator[LLMMessage]:
        request = self.build_request(
            messages=messages,
            tools=tools,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
            model=model,
            stream=True,
        )

        openai_messages = self._to_openai_messages(request.messages)
        kwargs: dict[str, Any] = {
            "model": request.model,
            "messages": openai_messages,
            "stream": True,
        }

        if request.tools:
            kwargs["tools"] = self._to_openai_tools(request.tools)
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens

        stream = await self.client.chat.completions.create(**kwargs)  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]

        accumulated_content = ""
        accumulated_tool_calls: dict[int, dict[str, str]] = {}

        async for chunk in stream:  # pyright: ignore[reportUnknownVariableType, reportUnknownArgumentType]
            choices = getattr(chunk, "choices", [])  # pyright: ignore[reportUnknownArgumentType]
            if not choices:
                continue

            delta = choices[0].delta  # pyright: ignore[reportUnknownMemberType]
            delta_content = getattr(delta, "content", None)
            delta_tool_calls = getattr(delta, "tool_calls", None)

            if delta_content:
                accumulated_content += cast(str, delta_content)

            if delta_tool_calls:
                for tc in delta_tool_calls:  # pyright: ignore[reportUnknownVariableType]
                    idx = cast(int, getattr(tc, "index", 0))
                    if idx not in accumulated_tool_calls:
                        accumulated_tool_calls[idx] = {"id": "", "name": "", "arguments": ""}

                    tc_id = getattr(tc, "id", None)
                    if tc_id:
                        accumulated_tool_calls[idx]["id"] = cast(str, tc_id)

                    tc_function = getattr(tc, "function", None)
                    if tc_function:
                        fn_name = getattr(tc_function, "name", None)
                        fn_args = getattr(tc_function, "arguments", None)
                        if fn_name:
                            accumulated_tool_calls[idx]["name"] = cast(str, fn_name)
                        if fn_args:
                            accumulated_tool_calls[idx]["arguments"] += cast(str, fn_args)

            tool_calls_list: list[LLMToolCall] | None = None
            if accumulated_tool_calls:
                tool_calls_list = [
                    LLMToolCall(
                        id=tc["id"],
                        name=tc["name"],
                        arguments=json.loads(tc["arguments"]) if tc["arguments"] else {},
                    )
                    for tc in accumulated_tool_calls.values()
                    if tc["id"] and tc["name"]
                ]

            yield LLMMessage.assistant(
                content=accumulated_content or None,
                tool_calls=tool_calls_list if tool_calls_list else None,
            )

    def build_request(
        self,
        messages: list[LLMMessage],
        tools: list[LLMToolDefinition] | None,
        system: str | None,
        temperature: float | None,
        max_tokens: int | None,
        model: str | None,
        stream: bool,
    ) -> ProviderChatRequest:
        provider_messages: list[ProviderMessage] = []

        if system:
            provider_messages.append(ProviderMessage(role="system", content=system))

        for msg in messages:
            provider_messages.extend(self._llm_message_to_provider(msg))

        provider_tools: list[ProviderTool] | None = None
        if tools:
            provider_tools = [
                ProviderTool(
                    function=ProviderToolFunction(
                        name=tool.name,
                        description=tool.description,
                        parameters=tool.parameters,
                    )
                )
                for tool in tools
            ]

        return ProviderChatRequest(
            model=model or self.config.model,
            messages=provider_messages,
            tools=provider_tools,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
        )

    def parse_response(self, response: ProviderChatResponse) -> LLMMessage:
        tool_calls: list[LLMToolCall] | None = None

        if response.tool_calls:
            tool_calls = [
                LLMToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments) if tc.function.arguments else {},
                )
                for tc in response.tool_calls
            ]

        return LLMMessage.assistant(content=response.content, tool_calls=tool_calls)

    def _llm_message_to_provider(self, msg: LLMMessage) -> list[ProviderMessage]:
        result: list[ProviderMessage] = []

        if msg.role.value == "user":
            result.append(ProviderMessage(role="user", content=msg.content or ""))

        elif msg.role.value == "assistant":
            tool_calls: list[ProviderToolCall] | None = None
            if msg.tool_calls:
                tool_calls = [
                    ProviderToolCall(
                        id=tc.id,
                        function=ProviderToolCallFunction(
                            name=tc.name,
                            arguments=json.dumps(tc.arguments),
                        ),
                    )
                    for tc in msg.tool_calls
                ]
            result.append(ProviderMessage(role="assistant", content=msg.content, tool_calls=tool_calls))

        elif msg.role.value == "tool_result":
            if msg.tool_results:
                for tr in msg.tool_results:
                    result.append(ProviderMessage(role="tool", content=tr.content, tool_call_id=tr.tool_call_id))

        return result

    def _to_openai_messages(self, messages: list[ProviderMessage]) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for msg in messages:
            openai_msg: dict[str, Any] = {"role": msg.role}

            if msg.content is not None:
                openai_msg["content"] = msg.content

            if msg.tool_calls:
                openai_msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in msg.tool_calls
                ]

            if msg.tool_call_id:
                openai_msg["tool_call_id"] = msg.tool_call_id

            result.append(openai_msg)
        return result

    def _to_openai_tools(self, tools: list[ProviderTool]) -> list[dict[str, Any]]:
        return [
            {
                "type": tool.type,
                "function": {
                    "name": tool.function.name,
                    "description": tool.function.description,
                    "parameters": tool.function.parameters,
                },
            }
            for tool in tools
        ]

    def _from_openai_response(self, response: Any) -> ProviderChatResponse:
        choices = getattr(response, "choices", [])
        if not choices:
            return ProviderChatResponse()

        message = choices[0].message  # pyright: ignore[reportUnknownMemberType]
        content = getattr(message, "content", None)
        raw_tool_calls = getattr(message, "tool_calls", None)

        tool_calls: list[ProviderToolCall] | None = None
        if raw_tool_calls:
            tool_calls = [
                ProviderToolCall(
                    id=cast(str, getattr(tc, "id", "")),
                    type=cast(str, getattr(tc, "type", "function")),
                    function=ProviderToolCallFunction(
                        name=cast(str, getattr(getattr(tc, "function", None), "name", "")),
                        arguments=cast(str, getattr(getattr(tc, "function", None), "arguments", "")),
                    ),
                )
                for tc in raw_tool_calls  # pyright: ignore[reportUnknownVariableType]
            ]

        return ProviderChatResponse(
            content=cast(str | None, content),
            tool_calls=tool_calls,
            finish_reason=cast(str | None, getattr(choices[0], "finish_reason", None)),
        )
