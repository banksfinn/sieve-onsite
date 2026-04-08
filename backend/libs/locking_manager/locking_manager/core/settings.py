import os

from pydantic_settings import BaseSettings


class LockingManagerSettings(BaseSettings):
    REDIS_URL: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")


locking_manager_settings = LockingManagerSettings()
