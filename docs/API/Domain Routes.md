# Domain Routes

All domain routes require authentication via `UserDependency`. Routes that create entities auto-set `user_id` and `created_by` from the authenticated user.

## Dataset Routes (`/api/gateway/dataset`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/dataset` | Search datasets (filter by name) |
| `GET` | `/dataset/{id}` | Get dataset by ID |
| `POST` | `/dataset` | Create dataset (optionally with bucket_path for auto-ingest) |
| `PATCH` | `/dataset/{id}` | Update dataset |
| `DELETE` | `/dataset/{id}` | Delete dataset |
| `POST` | `/dataset/{id}/ingest` | Ingest from GCS bucket (transitions requested → active) |
| `POST` | `/dataset/{id}/summarize-feedback` | Summarize all clip feedback for a dataset via LLM |

### Dataset Versions (`/api/gateway/dataset/{id}/version`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/dataset/{id}/version` | List versions for a dataset |
| `GET` | `/dataset/{id}/version/{vid}` | Get specific version |
| `GET` | `/dataset/{id}/version/{vid}/videos` | List videos in a version |
| `GET` | `/dataset/{id}/version/{vid}/clips` | List clips in a version |
| `POST` | `/dataset/{id}/version/{vid}/fork` | Fork a new version from selected clip subset |

### Clip Feedback (`/api/gateway/dataset/{id}/version/{vid}/clip/{cid}/feedback`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/dataset/{id}/version/{vid}/clip/{cid}/feedback` | List feedback for a clip in a version |
| `POST` | `/dataset/{id}/version/{vid}/clip/{cid}/feedback` | Submit clip feedback (timestamped, field-specific) |
| `PATCH` | `/dataset/{id}/version/{vid}/clip/{cid}/feedback/{fid}` | Update feedback (mark resolved, change rating) |

## Dataset Assignment Routes (`/api/gateway/dataset-assignment`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/dataset-assignment` | Search assignments (filter by dataset_id, user_id) |
| `POST` | `/dataset-assignment` | Assign user to dataset with role |
| `DELETE` | `/dataset-assignment/{id}` | Remove assignment |

## Video Routes (`/api/gateway/video`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/video` | Search videos (filter by delivery_id) |
| `GET` | `/video/{id}` | Get video by ID |
| `POST` | `/video` | Create video |

## Clip Routes (`/api/gateway/clip`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/clip` | Search clips (filter by video_id, dataset_version_id) |
| `GET` | `/clip/{id}` | Get clip by ID |
| `POST` | `/clip` | Create clip |

## Delivery Routes (`/api/gateway/delivery`)

> Note: Delivery exists in the backend but is not used in the current frontend flow. The review/feedback cycle happens on datasets directly. Delivery may be used in the future for shipping approved datasets to customers.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/delivery` | Search deliveries |
| `GET` | `/delivery/{id}` | Get delivery by ID |
| `POST` | `/delivery` | Create delivery |
| `PATCH` | `/delivery/{id}` | Update delivery |
| `DELETE` | `/delivery/{id}` | Delete delivery |

## See Also

- [[API Overview]] - Route registration and conventions
- [[Domain Models]] - Entity definitions
- [[OpenAPI Type Generation]] - Frontend type sync
