# Domain Routes

All domain routes require authentication via `UserDependency`. Routes that create entities auto-set `user_id` and `created_by` from the authenticated user.

## Dataset Routes (`/api/gateway/dataset`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/dataset` | Search datasets (filter by name) |
| `GET` | `/dataset/{id}` | Get dataset by ID |
| `POST` | `/dataset` | Create dataset |
| `PATCH` | `/dataset/{id}` | Update dataset |
| `DELETE` | `/dataset/{id}` | Delete dataset |
| `GET` | `/dataset/{id}/version` | List versions for a dataset |
| `GET` | `/dataset/{id}/version/{vid}` | Get specific version |
| `POST` | `/dataset/{id}/version` | Create new version (auto-sets `created_by`) |

## Video Routes (`/api/gateway/video`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/video` | Search videos (filter by delivery_id, source, language) |
| `GET` | `/video/{id}` | Get video by ID |
| `POST` | `/video` | Create video |

## Clip Routes (`/api/gateway/clip`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/clip` | Search clips (filter by video_id, dataset_version_id) |
| `GET` | `/clip/{id}` | Get clip by ID |
| `POST` | `/clip` | Create clip |

## Delivery Routes (`/api/gateway/delivery`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/delivery` | Search deliveries (filter by status, dataset_version_id, created_by) |
| `GET` | `/delivery/{id}` | Get delivery by ID |
| `POST` | `/delivery` | Create delivery (auto-sets `created_by`) |
| `PATCH` | `/delivery/{id}` | Update delivery (status transitions, description) |
| `DELETE` | `/delivery/{id}` | Delete delivery |

### Delivery Access (`/api/gateway/delivery/{id}/access`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/delivery/{id}/access` | List access entries for a delivery |
| `POST` | `/delivery/{id}/access` | Grant access to a user |
| `PATCH` | `/delivery/{id}/access/{aid}` | Update access role |
| `DELETE` | `/delivery/{id}/access/{aid}` | Revoke access |

### Delivery Feedback (`/api/gateway/delivery/{id}/feedback`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/delivery/{id}/feedback` | List delivery-level feedback |
| `POST` | `/delivery/{id}/feedback` | Submit verdict (approved/needs_changes/rejected) |

### Clip Feedback (`/api/gateway/delivery/{id}/clip/{cid}/feedback`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/delivery/{id}/clip/{cid}/feedback` | List feedback for a clip in a delivery |
| `POST` | `/delivery/{id}/clip/{cid}/feedback` | Submit clip feedback (timestamped, field-specific) |
| `PATCH` | `/delivery/{id}/clip/{cid}/feedback/{fid}` | Update feedback (mark resolved) |

## See Also

- [[API Overview]] - Route registration and conventions
- [[Domain Models]] - Entity definitions
- [[OpenAPI Type Generation]] - Frontend type sync
