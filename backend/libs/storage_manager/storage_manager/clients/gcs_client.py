import json

from google.cloud import storage
from google.oauth2 import service_account

from storage_manager.core.settings import storage_manager_settings


def _build_storage_client() -> storage.Client:
    """Build a GCS client, preferring in-memory credentials from GCS_CREDENTIALS_JSON."""
    creds_json = storage_manager_settings.GCS_CREDENTIALS_JSON
    if creds_json:
        info = json.loads(creds_json)
        credentials = service_account.Credentials.from_service_account_info(info)
        return storage.Client(credentials=credentials, project=info.get("project_id"))
    return storage.Client()


class GCSClient:
    def __init__(self, bucket_name: str | None = None):
        self._storage_client = _build_storage_client()
        self._bucket_name = bucket_name or storage_manager_settings.GCS_BUCKET_NAME
        self._bucket = self._storage_client.bucket(self._bucket_name)

    def list_blobs(self, prefix: str | None = None, delimiter: str | None = None) -> list[storage.Blob]:
        return list(self._storage_client.list_blobs(self._bucket_name, prefix=prefix, delimiter=delimiter))

    def get_blob(self, blob_path: str) -> storage.Blob | None:
        blob = self._bucket.blob(blob_path)
        if blob.exists():
            return blob
        return None

    def download_as_bytes(self, blob_path: str) -> bytes:
        blob = self._bucket.blob(blob_path)
        return blob.download_as_bytes()

    def download_as_string(self, blob_path: str) -> str:
        blob = self._bucket.blob(blob_path)
        return blob.download_as_text()

    def upload_from_string(self, blob_path: str, data: str, content_type: str = "application/json") -> storage.Blob:
        blob = self._bucket.blob(blob_path)
        blob.upload_from_string(data, content_type=content_type)
        return blob

    def upload_from_bytes(self, blob_path: str, data: bytes, content_type: str = "application/octet-stream") -> storage.Blob:
        blob = self._bucket.blob(blob_path)
        blob.upload_from_string(data, content_type=content_type)
        return blob

    def generate_signed_url(self, blob_path: str, expiration_minutes: int = 60) -> str:
        import datetime

        blob = self._bucket.blob(blob_path)
        return blob.generate_signed_url(expiration=datetime.timedelta(minutes=expiration_minutes))

    def delete_blob(self, blob_path: str) -> None:
        blob = self._bucket.blob(blob_path)
        blob.delete()

    def blob_exists(self, blob_path: str) -> bool:
        blob = self._bucket.blob(blob_path)
        return blob.exists()
