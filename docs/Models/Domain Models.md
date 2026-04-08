# Domain Models

The core domain is built around a **delivery-centric workflow**: datasets are versioned, deliveries scope feedback to a specific customer context, and feedback is timestamped and field-specific.

## Entity Relationship Diagram

```
Dataset (status: requested -> initialized -> active)
  └── DatasetVersion (versioned, with lineage)
        ├── DatasetVersionVideo[] (version 0: source video tracking)
        ├── Clip[] (version 1+: flattened metadata for filtering)
        │     └── ClipFeedback[] (scoped to delivery, timestamped, field-specific)
        └── Delivery[] (workflow state machine)
              ├── DeliveryAccess[] (role-based per user)
              └── DeliveryFeedback[] (delivery-level verdicts)

Video (source videos, deduplicated by delivery_id)
  ├── Clip[]
  └── DatasetVersionVideo[]
```

## Key Design Decisions

### Feedback is scoped to Delivery, not Clip globally

The same clip can appear in multiple deliveries and be judged differently per customer. `ClipFeedback.delivery_id` ensures feedback is contextual.

### DatasetVersion is separate from Dataset

Enables lineage tracking (`parent_version_id`), version diffing, and reuse across deliveries. A delivery references a specific version, not the dataset directly.

### Clip metadata is flattened, not a separate table

Fields like `avg_face_size`, `max_num_faces`, `is_full_body`, `has_overlay` are columns on `Clip`, not a key-value table. This is intentional: the primary use case is heavy filtering, and flattened columns give us query performance and type safety.

### Dataset has its own lifecycle

`DatasetStatus` tracks ingestion progress: `requested` -> `initialized` -> `active`. See [[Dataset Lifecycle]] for details on version 0 (source videos) vs version 1+ (clips).

### Delivery status is a state machine

`DeliveryStatus` tracks the customer review workflow: `draft` -> `sent_to_customer` -> `in_review` -> `feedback_received` -> `iterating` -> `ready_for_approval` -> `approved`/`rejected`.

State lives at the **delivery level**, not per-clip. Individual clips get feedback ratings, but the delivery moves through states as a unit.

### ClipFeedback supports timestamped, field-specific issues

- `timestamp`: pinpoints when in the video the issue occurs
- `metadata_field`: links feedback to a specific metadata field (e.g. "avg_face_size is wrong")
- `resolved_in_version_id` + `is_resolved`: tracks issue resolution across versions

## Models Reference

| Model | File | Key Fields |
|-------|------|-----------|
| Dataset | `app/blueprints/dataset.py` | name, description, status, bucket_path |
| DatasetVersion | `app/blueprints/dataset.py` | dataset_id, version_number, parent_version_id, created_by |
| DatasetVersionVideo | `app/blueprints/dataset.py` | dataset_version_id, video_id |
| Video | `app/blueprints/video.py` | delivery_id, uri, fps, height, width, source, language |
| Clip | `app/blueprints/clip.py` | video_id, dataset_version_id, uri, start/end_time, duration, avg_face_size, max_num_faces, is_full_body, has_overlay |
| Delivery | `app/blueprints/delivery.py` | dataset_version_id, customer_request_description, created_by, status |
| DeliveryAccess | `app/blueprints/delivery_access.py` | delivery_id, user_id, role |
| ClipFeedback | `app/blueprints/clip_feedback.py` | clip_id, delivery_id, user_id, rating, comment, timestamp, metadata_field, is_resolved, resolved_in_version_id |
| DeliveryFeedback | `app/blueprints/delivery_feedback.py` | delivery_id, user_id, status, summary |

## See Also

- [[Data Model Overview]] - Blueprint pattern and type hierarchy
- [[Blueprint Pattern]] - Entity definition convention
- [[API Overview]] - Route registration
- [[Dataset Lifecycle]] - Dataset status machine and version 0 concept
