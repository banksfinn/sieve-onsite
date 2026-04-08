import os

from fullstack_types.environments import Environment
from pydantic_settings import BaseSettings


class DatabaseManagerSettings(BaseSettings):
    ENVIRONMENT: Environment = Environment(os.environ["ENV"])
    DATABASE_URL: str = os.environ["DATABASE_URL"]

    VERBOSE_DATABASE_MODE: bool = False


database_manager_settings = DatabaseManagerSettings()
