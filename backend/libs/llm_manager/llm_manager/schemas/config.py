"""Configuration schemas for the LLM manager library."""

from pydantic import BaseModel, Field, SecretStr


class LLMRetryConfig(BaseModel):
    """Configuration for retry behavior."""

    max_retries: int = Field(default=3, ge=0)
    initial_delay: float = Field(default=1.0, gt=0)
    max_delay: float = Field(default=30.0, gt=0)
    exponential_base: float = Field(default=2.0, gt=1)


class LLMTimeoutConfig(BaseModel):
    """Configuration for timeout behavior."""

    connect_timeout: float = Field(default=10.0, gt=0)
    read_timeout: float = Field(default=120.0, gt=0)


class LLMProviderConfig(BaseModel):
    """Configuration for an LLM provider."""

    api_key: SecretStr = Field(...)
    retry: LLMRetryConfig = Field(default_factory=LLMRetryConfig)
    timeout: LLMTimeoutConfig = Field(default_factory=LLMTimeoutConfig)
    base_url: str | None = Field(default=None)
    model: str = Field(default="gpt-4o")
