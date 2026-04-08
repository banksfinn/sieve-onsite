# Dataset Lifecycle

The dataset lifecycle tracks ingestion progress from initial request through active iteration. This is separate from the [[Domain Models|Delivery status machine]], which tracks the customer review workflow.

## States

```
requested -> initialized -> active
```

| Status | Meaning | Who triggers |
|--------|---------|-------------|
| `requested` | Dataset created, no data yet | Customer or GTM (via dataset creation) |
| `initialized` | Bucket path + video metadata provided, version 0 exists | Researcher (via initialize endpoint) or GTM (at creation time) |
| `active` | At least one clip version (v1+) exists | Researcher (auto-advanced on first clip upload) |

No backward transitions. Once initialized, a dataset cannot return to `requested`.

## Version 0 vs Version 1+

**Version 0 (Initialization)**
- Created during dataset initialization
- Contains source video references only (no clips)
- Videos tracked via `dataset_version_videos` join table
- Represents "here are the raw videos we're working with"

**Version 1+ (Clip Versions)**
- Created when researcher uploads clip metadata
- Contains clips extracted from the source videos
- Each version auto-increments from the previous
- `parent_version_id` links to the previous version for lineage

## Key Design Decisions

### DB is a curated subset, not a GCS mirror

Videos are only created in Postgres when referenced by metadata. The system never syncs an entire GCS bucket. This keeps the database aligned with what users actually care about (datasets and clips), not raw storage contents.

### Videos are deduplicated by `delivery_id`

The same video (identified by `delivery_id`) can appear across multiple datasets. Videos are found-or-created during ingestion — if a video with that `delivery_id` already exists, it's reused.

### Signed URLs are the boundary

The system stores `gs://` URIs and generates signed URLs on demand for playback. Video bytes never pass through the backend.

## GTM Fast Path

When GTM creates a dataset on behalf of a customer, they can provide `bucket_path` and `videos` at creation time. This skips the `requested` state and goes directly to `initialized`.

## Relationship to DeliveryStatus

| Concern | Tracked by |
|---------|-----------|
| Ingestion progress (do we have data?) | `DatasetStatus` on Dataset |
| Customer review workflow | `DeliveryStatus` on Delivery |

A Delivery references a specific DatasetVersion. The delivery workflow (draft -> sent -> review -> feedback -> approved) operates independently of the dataset lifecycle.

## See Also

- [[Domain Models]]
- [[User Flows]]
- [[Product Notes]]
