import os
from urllib.parse import urlparse

from fullstack_types.environments import Environment
from pydantic_settings import BaseSettings


class UserManagementSettings(BaseSettings):
    ENVIRONMENT: Environment = Environment(os.environ["ENV"])
    DATABASE_URL: str = os.environ["DATABASE_URL"]
    FRONTEND_URL: str = os.environ.get("FRONTEND_URL", "http://localhost:1300")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    TOKEN_SECRET_KEY: str = os.environ["TOKEN_SECRET_KEY"]
    TOKEN_KEY_IDENTIFIER: str = os.environ["TOKEN_KEY_IDENTIFIER"]

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


settings = UserManagementSettings()
