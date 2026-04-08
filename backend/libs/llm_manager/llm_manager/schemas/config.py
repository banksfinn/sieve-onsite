"""Configuration schemas for the LLM manager library."""

from pydantic import BaseModel, Field, SecretStr


class LLMRetryConfig(BaseModel):
    """Configuration for retry behavior."""

    max_retries: int = Field(default=3, ge=0, description="Maximum number of retry attempts")
    initial_delay: float = Field(default=1.0, gt=0, description="Initial delay in seconds before first retry")
    max_delay: float = Field(default=30.0, gt=0, description="Maximum delay in seconds between retries")
    exponential_base: float = Field(default=2.0, gt=1, description="Base for exponential backoff calculation")


class LLMTimeoutConfig(BaseModel):
    """Configuration for timeout behavior."""

    connect_timeout: float = Field(default=10.0, gt=0, description="Timeout in seconds for connection establishment")
    read_timeout: float = Field(default=120.0, gt=0, description="Timeout in seconds for reading response")


class LLMProviderConfig(BaseModel):
    """Configuration for an LLM provider."""

    api_key: SecretStr = Field(..., description="API key for the provider")
    retry: LLMRetryConfig = Field(default_factory=LLMRetryConfig, description="Retry configuration")
    timeout: LLMTimeoutConfig = Field(default_factory=LLMTimeoutConfig, description="Timeout configuration")
    base_url: str | None = Field(default=None, description="Optional base URL override (for proxies)")
    model: str = Field(default="gpt-4o", description="Default model to use")
