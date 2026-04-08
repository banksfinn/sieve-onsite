import os
from urllib.parse import urlparse

from sieve_types.environments import Environment
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: Environment = Environment(os.environ.get("ENV", "local"))
    TOKEN_KEY_IDENTIFIER: str = os.environ["TOKEN_KEY_IDENTIFIER"]
    TOKEN_SIGNING_SECRET: str = os.environ["TOKEN_SIGNING_SECRET"]
    FRONTEND_URL: str = os.environ.get("FRONTEND_URL", "http://localhost:1300")
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")

    @property
    def is_deployed(self) -> bool:
        return self.ENVIRONMENT == Environment.deploy

    @property
    def cookie_domain(self) -> str | None:
        """Extract domain from FRONTEND_URL for cookie setting in deployed environments."""
        if not self.is_deployed:
            return None
        parsed = urlparse(self.FRONTEND_URL)
        return parsed.hostname


settings = Settings()
