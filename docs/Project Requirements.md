# Project Requirements

Full requirements at `docs/project_requirements.md`.

## Problem

GTM and Engineering teams at Sieve need to collaborate on video sample review. Current workflow is manual:

1. GTM receives a sample bucket and metadata bucket
2. GTM downloads videos from bucket to view locally
3. Metadata must be searched separately
4. Feedback given back to engineering through unstructured channels

This is slow and adds iteration time to deal closures.

## Solution

Build an end-to-end product that:

- Ingests from `gs://product-onsite/` bucket (videos + JSON metadata)
- Provides UI for sending samples to customers
- Allows customers to view videos with associated metadata
- Supports video-specific feedback from customers
- Enables GTM to review and act on feedback
- Makes samples updatable

## Data Model

### Clip Metadata

```json
{
    "delivery_id": "y_VMplMXoqnaY",
    "uri": "gs://mybucket/videos/y_VMplMXoqnaY_clip_1.mp4",
    "clip_start_time": 1.23,
    "clip_end_time": 5.23,
    "clip_duration": 4.00,
    "avg_face_size": 125,
    "max_num_faces": 2
}
```

### Video Metadata

```json
{
    "delivery_id": "y_b9plMXe89G",
    "fps": 29.9,
    "height": 1080,
    "width": 1920,
    "source": "web",
    "language": "en"
}
```

Key relationship: Clips belong to a video (shared `delivery_id`). A video can have many clips with different time ranges.

## Evaluation Criteria

- Thorough understanding of the problem
- Engineering principles
- UI/UX for both GTM and Engineering
- Ability to communicate the solution

## Design Considerations

- **Speed**: Review process should be fluid and fast
- **Feedback quality**: Engineers need actionable, specific feedback
- **Workflow**: GTM gets buckets and metadata files; system should streamline from there

## See Also

- [[Architecture Overview]]
- [[GCSClient]]
- [[Data Model Overview]]
