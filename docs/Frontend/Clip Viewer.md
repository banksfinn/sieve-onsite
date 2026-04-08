# Clip Viewer

The clip viewer (`ClipViewerPage.tsx`) is the core review experience. It provides a rich, three-panel interface for reviewing individual video clips with time-synced metadata and contextual feedback.

Route: `/delivery/:deliveryId/clip/:clipId`

## Layout

```
┌──────────────┬───────────────────────────┬──────────────┐
│  Metadata    │     Video Player          │  Issues      │
│  Panel       │     + Timeline            │  Panel       │
│  (272px)     │     + Feedback Form       │  (320px)     │
│              │                           │              │
│  - Fields    │  ┌─────────────────────┐  │  - Feedback  │
│  - Progress  │  │   <video>           │  │    items     │
│  - Boundary  │  │                     │  │  - Resolve   │
│    adjuster  │  └─────────────────────┘  │    toggle    │
│              │  [feedback timeline bar]  │  - Show/hide │
│              │  [feedback form]          │    resolved  │
└──────────────┴───────────────────────────┴──────────────┘
```

## Features

### Time-Synced Metadata (Left Panel)
- Clip metadata fields displayed as clickable buttons
- Progress bar showing position within the clip's source video range
- Source video timestamp updates live during playback
- Clicking a field highlights it and pre-fills the feedback form's "linked field" selector

### Video Player + Feedback Timeline (Center)
- HTML5 video with `onTimeUpdate` tracking current position
- Feedback timeline scrubber showing colored dots for each timestamped feedback item
- Current time indicator line on the timeline
- Clicking a dot seeks the video to that timestamp

### Feedback Form (Center, below video)
- Good/Bad/Unsure rating buttons
- "Pin timestamp" captures current video position
- Metadata field dropdown links feedback to a specific field
- Comment textarea
- All fields are optional except rating

### Issue Resolution (Right Panel)
- List of all feedback items with rating badge, metadata field tag, timestamp link
- Clicking timestamp seeks video to that point
- Circle/checkmark toggle marks issues as resolved
- `resolved_in_version_id` tracks which version fixed the issue
- "Show/hide resolved" filter

### Boundary Adjustment (Left Panel, collapsible)
- Start/end time inputs for GTM/researchers to suggest clip boundary changes
- Shows delta from original boundaries
- Duration auto-calculated

### Version Selector (Header)
- Button group for each dataset version (v1, v2, etc.)
- Allows flipping between versions to compare the same clip across iterations

## Component Structure

```
ClipViewerPage
  ├── MetadataPanel (time-synced, clickable fields)
  ├── BoundaryAdjuster (collapsible)
  ├── <video> (with ref for time tracking)
  ├── Feedback Timeline (marker dots)
  ├── FeedbackForm (rating, timestamp, field, comment)
  ├── FeedbackItem[] (resolve toggle, seek link)
  └── VersionSelector (dataset version buttons)
```

## Data Flow

1. `useGetClip(clipId)` fetches clip data
2. `useSearchClipFeedback(deliveryId, clipId)` fetches all feedback
3. Video `onTimeUpdate` drives `MetadataPanel` progress bar
4. Feedback form captures timestamp via `videoRef.current.currentTime`
5. `useCreateClipFeedback` submits, then invalidates feedback query
6. `useUpdateClipFeedback` marks resolved, then invalidates feedback query

## See Also

- [[Domain Models]] - ClipFeedback schema with timestamp, metadata_field, resolution fields
- [[Domain Routes]] - Clip feedback API endpoints
- [[Component Library]] - shadcn/ui components used
