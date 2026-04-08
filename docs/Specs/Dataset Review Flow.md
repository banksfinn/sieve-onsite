# Dataset Review Flow

Spec for the GTM/customer review workflow that replaces the delivery-centric feedback model with a version-centric review system directly on datasets.

## Problem

The current review experience has several gaps:
- No clear "Review" affordance on dataset detail — the pencil icon reads as "edit"
- No aggregate feedback status per version
- No dataset-level verdict (old delivery feedback was removed)
- No structured flow for researchers to address reviewer comments between versions
- Customer role can't access the Datasets nav link

## Core Concepts

### Reviews vs Feedback

The existing `ClipFeedback` model captures clip-level quality signals (good/bad/unsure + timestamp + metadata field). **Reviews** are a higher-level construct:

| Concept | Scope | Who | Purpose |
|---------|-------|-----|---------|
| ClipFeedback | Single clip, single field | Any reviewer | "This metadata value is wrong at 0:14" |
| Review | Dataset version (may reference a clip) | GTM / Customer | "This clip should be removed" or "Overall, the face detection needs work" |

Reviews are **threaded conversations** with a lifecycle, not point-in-time ratings.

### Version Commit Messages

Each `DatasetVersion` (v1+) gets a required `commit_message` — a single-line description of what changed. This provides context when hovering version chips on reviews.

Examples:
- "Initial clip extraction from 47 source videos"
- "Removed 12 clips with overlay artifacts, adjusted face size thresholds"
- "Re-extracted clips 34-41 with corrected boundaries"

## Data Model Changes

### DatasetVersion — add `commit_message`

```python
class DatasetVersionModel(BaseEntityModel):
    # ... existing fields ...
    commit_message: Mapped[str | None] = mapped_column(String, nullable=True)
```

v0 (initialization) won't have a commit message. v1+ should.

### DatasetReview — new entity

A review is a top-level comment on a dataset version, optionally scoped to a specific clip.

```python
class DatasetReviewModel(BaseEntityModel):
    __tablename__ = "dataset_reviews"

    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"))
    dataset_version_id: Mapped[int] = mapped_column(ForeignKey("dataset_versions.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # "review" or "request_for_deletion"
    review_type: Mapped[str] = mapped_column(String, nullable=False)

    # Optional clip scope — null means dataset-level comment
    clip_id: Mapped[int | None] = mapped_column(ForeignKey("clips.id"), nullable=True)

    # Timestamp in the clip where the issue is visible (for clip-scoped reviews)
    clip_timestamp: Mapped[float | None] = mapped_column(Float, nullable=True)

    comment: Mapped[str] = mapped_column(Text, nullable=False)

    # Lifecycle: open -> closed | auto_completed
    status: Mapped[str] = mapped_column(String, nullable=False, default="open")

    # If this review was resolved in a specific version
    resolved_in_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("dataset_versions.id"), nullable=True
    )
```

### DatasetReviewReply — new entity

Threaded replies on a review. Both reviewer and researcher can reply.

```python
class DatasetReviewReplyModel(BaseEntityModel):
    __tablename__ = "dataset_review_replies"

    review_id: Mapped[int] = mapped_column(ForeignKey("dataset_reviews.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    comment: Mapped[str] = mapped_column(Text, nullable=False)
```

### New Enums

```python
class ReviewType(str, Enum):
    review = "review"
    request_for_deletion = "request_for_deletion"

class ReviewStatus(str, Enum):
    open = "open"
    closed = "closed"
    auto_completed = "auto_completed"
```

## User Flows

### Flow 1: GTM/Customer Reviews a Dataset Version

1. From **Dataset Detail**, click **"Review"** button on the latest version (or any v1+ version)
2. Lands on **Version Review Page** (`/dataset/:id/version/:vid/review`)
3. Sees a **clip table** showing all clips with:
   - Clip filename, duration, key metadata badges
   - Review status indicator: no reviews / has open reviews / all resolved
   - Click to expand inline or navigate to clip viewer
4. Can leave **top-level reviews** (dataset-wide comments) via a form at the top
5. Can leave **clip-scoped reviews** by clicking a clip row and using the inline review form
6. Each review form has:
   - Type selector: "Review" (default) or "Request for Deletion"
   - Comment text (required)
   - Timestamp pin (for clip-scoped reviews, references clip playback time)
7. All reviews are tagged with the current `dataset_version_id`

### Flow 2: Viewing Reviews with Version Context

When viewing a review (in the review list or in the active comments flow):
- A **version chip** (e.g., "v2") is displayed next to the review
- **Hovering** the chip shows a tooltip with the commit messages for that version and subsequent versions
- This gives the reviewer context: "this comment was made against v2, which was 'Initial extraction'. We're now on v4."

### Flow 3: Researcher Submits a New Version (Active Comments Flow)

When a researcher uploads new clip metadata / forks a version:

1. After the version is created, they enter the **Active Comments** flow
2. This is a dedicated page: `/dataset/:id/version/:vid/review-comments`
3. Shows all **open reviews** from the previous version(s), organized as:
   - **Top-level comments first** (dataset-wide reviews)
   - **Then clip-by-clip** — grouped by clip, with the clip's reviews listed under it
4. For each review, the researcher can:
   - **Close** it (green checkmark) — marks as `closed`, still visible but greyed
   - **Reply** to continue the discussion
   - **Auto-completed** reviews are highlighted — these are "Request for Deletion" reviews where the referenced clip was removed in this version. The system detects this automatically.
5. If a review references a clip that **no longer exists** in the new version:
   - The review is elevated to the top-level section
   - Marked with a "Clip removed" indicator
   - If it was a "Request for Deletion" → auto-completed
   - If it was a "Review" → still open, researcher must address it
6. The researcher can **switch to clip-by-clip view** to browse clips with their associated reviews in the clip viewer

### Flow 4: Review Lifecycle Across Versions

```
v1: Customer leaves 5 reviews (3 reviews, 2 deletion requests)
                    ↓
v2: Researcher creates new version
    → Auto-complete: 1 deletion request (clip was removed)
    → Researcher closes 2 reviews with replies explaining changes
    → 2 reviews remain open (carried forward)
                    ↓
v3: Customer sees the carried-forward reviews still open
    → Leaves 1 new review
    → Total open: 3
```

Reviews **persist across versions**. They are tagged with the version they were created on but remain visible until explicitly closed or auto-completed.

## API Endpoints

### Dataset Reviews (`/api/gateway/dataset/{id}/version/{vid}/review`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/dataset/{id}/review` | Search all reviews for a dataset (filter by version, status, clip, type) |
| `GET` | `/dataset/{id}/version/{vid}/review` | Reviews for a specific version |
| `POST` | `/dataset/{id}/version/{vid}/review` | Create a review |
| `PATCH` | `/dataset/{id}/review/{rid}` | Update review (close, add resolved_in_version_id) |

### Review Replies (`/api/gateway/dataset/{id}/review/{rid}/reply`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/dataset/{id}/review/{rid}/reply` | List replies for a review |
| `POST` | `/dataset/{id}/review/{rid}/reply` | Add a reply |

### Dataset Version — updated

| Method | Path | Change |
|--------|------|--------|
| `POST` | `/dataset/{id}/version` | Now requires `commit_message` for v1+ |

### Active Comments Summary

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/dataset/{id}/version/{vid}/active-comments` | Returns open reviews from prior versions, with auto-completion status computed |

## Frontend Pages

### New: Version Review Page

Route: `/dataset/:datasetId/version/:versionId/review`

For GTM/Customer to review a specific version. Shows clip table with review status and forms for creating reviews.

### New: Active Comments Page

Route: `/dataset/:datasetId/version/:versionId/review-comments`

For Researchers after creating a new version. Walk through open comments, close/reply/auto-complete.

### Modified: Dataset Detail Page

- Add **"Review"** button next to each v1+ version (alongside existing pencil/edit button)
- Add review summary per version: "3 open reviews, 2 resolved"
- Add overall dataset review summary card

### Modified: Version Editor Page

- After forking a version, prompt for **commit message** before creating
- After creation, navigate to Active Comments page instead of back to dataset detail

## Auto-Completion Logic

When computing active comments for a new version:

```
for each open review from prior versions:
    if review.clip_id is not None:
        if review.clip_id NOT IN new_version_clip_ids:
            if review.review_type == "request_for_deletion":
                → mark as auto_completed, set resolved_in_version_id
            else:
                → elevate to top-level (clip removed but comment stands)
```

This runs server-side when the active comments endpoint is called for a new version.

## Migration Plan

1. Add `commit_message` to `dataset_versions` table
2. Create `dataset_reviews` table
3. Create `dataset_review_replies` table
4. Add new enums
5. Backend: blueprints, stores, routes
6. Frontend: new pages, modified pages
7. `make sync_openapi` to generate types

## Decided Questions

- **ClipFeedback/DeliveryFeedback**: Reviews subsume both. ClipFeedback functionality (ratings, timestamps, metadata field references) is absorbed into `DatasetReview`. The old models remain in the DB but are not used by new flows. No migration of existing data needed — the old clip viewer feedback still works for historical data.
- **Customer visibility**: Customers can see all reviews. Reviews are not role-gated.
- **Notifications**: Not in scope for this iteration.

## See Also

- [[Domain Models]] - Current entity relationships
- [[Dataset Lifecycle]] - Version numbering and status machine
- [[Clip Viewer]] - Existing clip review experience
- [[User Flows]] - Current user journeys by role
- [[Product Notes]] - Business rules
