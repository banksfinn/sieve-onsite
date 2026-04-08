# GCSClient

Google Cloud Storage client wrapper at `backend/libs/storage_manager/storage_manager/clients/gcs_client.py`.

## Responsibilities

Provides a simplified interface over `google.cloud.storage` for common blob operations.

## API

| Method | Purpose |
|--------|---------|
| `list_blobs(prefix, delimiter)` | List blobs in the bucket |
| `get_blob(blob_path)` | Get blob if it exists, else None |
| `download_as_bytes(blob_path)` | Download blob content as bytes |
| `download_as_string(blob_path)` | Download blob content as text |
| `upload_from_string(blob_path, data, content_type)` | Upload string data |
| `upload_from_bytes(blob_path, data, content_type)` | Upload binary data |
| `generate_signed_url(blob_path, expiration_minutes)` | Generate time-limited access URL |
| `delete_blob(blob_path)` | Delete a blob |
| `blob_exists(blob_path)` | Check if blob exists |

## Configuration

| Setting | Source | Default |
|---------|--------|---------|
| `GCS_BUCKET_NAME` | env var | Required |

The bucket can also be overridden per-instance via the constructor:

```python
client = GCSClient(bucket_name="product-onsite")
```

## Usage Context

The [[Project Requirements]] specify video samples stored at `gs://product-onsite/`. This client is used to:

- List available videos and metadata files
- Download metadata JSON for display
- Generate signed URLs for video playback in the browser
- Upload updated sample sets

## Signed URLs

`generate_signed_url()` creates time-limited URLs (default 60 minutes) that allow unauthenticated access to blobs. This is critical for serving video content to the frontend without proxying through the backend.

## File Location

`backend/libs/storage_manager/storage_manager/clients/gcs_client.py`

## See Also

- [[Architecture Overview]]
- [[Project Requirements]]
- [[Backend Architecture]]
