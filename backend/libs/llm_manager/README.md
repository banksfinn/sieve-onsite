# LLM Manager

A reusable foundation for LLM-powered applications with tool calling.

## Features

- **SDK-based**: Uses official provider SDKs (OpenAI)
- **Async-first**: All I/O operations are async
- **Type-safe**: Full type hints with Pydantic models for validation
- **Prefixed types**: All public types prefixed with `LLM` to avoid namespace pollution
- **Extensible**: Abstract provider interface for adding providers

## Usage

```python
from llm_manager import (
    LLMConversationLoop,
    LLMProviderConfig,
    LLMToolExecutor,
    OpenAIProvider,
)

# Configure provider
config = LLMProviderConfig(api_key="your-key")
provider = OpenAIProvider(config)

# Create executor and register tools
executor = LLMToolExecutor()
# executor.register(your_tool_handler)

# Create conversation loop
loop = LLMConversationLoop(
    provider=provider,
    executor=executor,
    system_prompt="You are a helpful assistant.",
)

# Run conversation
response = await loop.run(
    user_input="Hello!",
    context=LLMToolContext(),
)
```
