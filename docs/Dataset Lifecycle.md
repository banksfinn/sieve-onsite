# Dataset Lifecycle

Datasets have two independent state dimensions: **lifecycle** (does it have data?) and **request status** (where is it in the customer iteration cycle?).

## Lifecycle States

Tracks whether the dataset has data available.

```
pending -> active -> archived
```

| Lifecycle | Meaning | Who triggers |
|-----------|---------|-------------|
| `pending` | Dataset created, no data ingested yet | System default on creation |
| `active` | Data exists (videos/clips ingested) | System (auto-set on successful ingestion) |
| `archived` | Dataset retired, read-only | GTM or Admin (manual) |

No backward transitions from `active`. `archived` is terminal.

## Request Status States

Tracks the customer iteration/delivery cycle.

```
requested -> in_progress -> review_requested -> approved
                  ^                |
                  |                v
                  +---- changes_requested

(any non-terminal) -----> rejected
```

| Request Status | Meaning | Who triggers |
|----------------|---------|-------------|
| `requested` | Customer/GTM created the request, awaiting work | Customer or GTM (on creation) |
| `in_progress` | Researcher is actively working on the dataset | Researcher (on ingest or after addressing feedback) |
| `review_requested` | A version is ready for customer/GTM review | Researcher (explicit signal) |
| `changes_requested` | Reviewer wants modifications | GTM or Customer (after reviewing) |
| `approved` | Dataset is satisfactory, work complete | GTM or Customer |
| `rejected` | Dataset request won't be fulfilled | GTM or Customer |

Terminal states: `approved` and `rejected`.

## How the Two Dimensions Interact

| Scenario | Lifecycle | Request Status |
|----------|-----------|---------------|
| Customer submits a new request | `pending` | `requested` |
| GTM creates dataset with bucket path (fast path) | `active` | `in_progress` |
| Researcher ingests data into a pending dataset | `active` | `in_progress` |
| Researcher signals version is ready for review | `active` | `review_requested` |
| Customer requests changes after reviewing | `active` | `changes_requested` |
| Researcher addresses feedback, re-submits | `active` | `review_requested` |
| Customer approves the dataset | `active` | `approved` |
| Approved dataset is retired | `archived` | `approved` |

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

When GTM creates a dataset on behalf of a customer, they can provide `bucket_path` and `videos` at creation time. This skips the `pending` lifecycle state and goes directly to `active` with request status `in_progress`.

## Review and Feedback

The review/feedback cycle happens directly on datasets and versions — there is no separate delivery workflow. ClipFeedback is scoped to `dataset_id` + `dataset_version_id`, and tracks resolution across versions via `resolved_in_version_id`.

| Concern | Tracked by |
|---------|-----------|
| Data availability | `DatasetLifecycle` on Dataset |
| Iteration/delivery cycle | `DatasetRequestStatus` on Dataset |
| Clip-level review feedback | `ClipFeedback` scoped to dataset version |
| Threaded review conversations | `DatasetReview` + `DatasetReviewReply` |
| Issue resolution across versions | `ClipFeedback.resolved_in_version_id` + `is_resolved` |

## See Also

- [[Domain Models]]
- [[User Flows]]
- [[Product Notes]]
