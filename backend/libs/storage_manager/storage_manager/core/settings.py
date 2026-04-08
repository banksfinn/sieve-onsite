import os

from pydantic_settings import BaseSettings


class StorageManagerSettings(BaseSettings):
    GCS_BUCKET_NAME: str = os.environ.get("GCS_BUCKET_NAME", "")
    GOOGLE_APPLICATION_CREDENTIALS: str = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")


storage_manager_settings = StorageManagerSettings()
