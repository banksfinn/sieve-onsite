# Domain Models

The core domain is built around a **dataset-centric workflow**: datasets are versioned, feedback is scoped to a dataset version, and the review cycle happens directly on clips within versions.

## Entity Relationship Diagram

```
Dataset (lifecycle: pending/active/archived, request_status: requested/in_progress/review_requested/changes_requested/approved/rejected)
  ├── DatasetAssignment[] (user-to-dataset with role)
  ├── DatasetReview[] (threaded, versioned, optionally clip-scoped)
  │     └── DatasetReviewReply[] (conversation thread)
  └── DatasetVersion (versioned, with lineage + commit_message)
        ├── DatasetVersionVideo[] (version 0: source video tracking)
        ├── Clip[] (version 1+: flattened metadata for filtering)
        │     └── ClipFeedback[] (legacy — scoped to dataset + version, timestamped, field-specific)
        └── (Delivery[] — exists in backend for future "ship to customer" use, not in frontend flow)

Video (source videos, deduplicated by delivery_id)
  ├── Clip[]
  └── DatasetVersionVideo[]
```

## Key Design Decisions

### Feedback is scoped to Dataset + Version

ClipFeedback has both `dataset_id` and `dataset_version_id`, allowing feedback to be queried across all versions of a dataset or filtered to a specific version. The iteration cycle (leave feedback → create new version → mark feedback resolved) lives entirely within the dataset.

### DatasetVersion is separate from Dataset

Enables lineage tracking (`parent_version_id`), version diffing, and forking subsets of clips into new versions. Researchers review clips within a version, leave feedback, then fork a new version with adjustments.

### Clip metadata uses JSONB extra_metadata

Clip-specific metadata (face detection scores, overlay flags, etc.) is stored in a `extra_metadata` JSONB column on Clip, not as separate columns. This allows flexible metadata schemas across different dataset types while still supporting filtering.

### Dataset has two state dimensions

`DatasetLifecycle` tracks data availability: `pending` -> `active` -> `archived`. `DatasetRequestStatus` tracks the customer iteration cycle: `requested` -> `in_progress` -> `review_requested` -> `approved` (with `changes_requested` and `rejected` branches). See [[Dataset Lifecycle]] for the full state diagram.

### ClipFeedback supports timestamped, field-specific issues

- `timestamp`: pinpoints when in the video the issue occurs
- `metadata_field`: links feedback to a specific metadata field (e.g. "avg_face_size is wrong")
- `resolved_in_version_id` + `is_resolved`: tracks issue resolution across versions

### Delivery is reserved for final output (not iteration)

The Delivery model exists in the backend but is not part of the current frontend flow. The iteration/feedback cycle happens on datasets directly. Delivery may be used in the future for the "ship approved dataset to customer" step.

## Models Reference

| Model | File | Key Fields |
|-------|------|-----------|
| Dataset | `app/blueprints/dataset.py` | name, description, lifecycle, request_status, bucket_path |
| DatasetVersion | `app/blueprints/dataset.py` | dataset_id, version_number, parent_version_id, created_by, commit_message |
| DatasetVersionVideo | `app/blueprints/dataset.py` | dataset_version_id, video_id |
| DatasetAssignment | `app/blueprints/dataset_assignment.py` | dataset_id, user_id, role |
| Video | `app/blueprints/video.py` | delivery_id, uri, fps, height, width, extra_metadata |
| Clip | `app/blueprints/clip.py` | video_id, dataset_version_id, uri, start/end_time, duration, extra_metadata |
| ClipFeedback | `app/blueprints/clip_feedback.py` | clip_id, dataset_id, dataset_version_id, user_id, rating, comment, timestamp, metadata_field, is_resolved, resolved_in_version_id |
| DatasetReview | `app/blueprints/dataset_review.py` | dataset_id, dataset_version_id, user_id, review_type, clip_id, clip_timestamp, comment, status, resolved_in_version_id |
| DatasetReviewReply | `app/blueprints/dataset_review.py` | review_id, user_id, comment |

## See Also

- [[Data Model Overview]] - Blueprint pattern and type hierarchy
- [[Blueprint Pattern]] - Entity definition convention
- [[API Overview]] - Route registration
- [[Dataset Lifecycle]] - Dataset status machine and version 0 concept
