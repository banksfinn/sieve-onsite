"""LLM Manager settings from environment."""

from pydantic_settings import BaseSettings


class LLMManagerSettings(BaseSettings):
    """Settings for the LLM manager loaded from environment."""

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_BASE_URL: str | None = None

    class Config:
        env_prefix = ""
        case_sensitive = True


llm_settings = LLMManagerSettings()
