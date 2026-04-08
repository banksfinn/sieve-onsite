"""Ingest dataset metadata from a GCS bucket.

Reads clip_metadata.jsonl and video_metadata.jsonl from a bucket prefix,
splits each row into common DB columns + extra_metadata JSONB.
"""

import json
from dataclasses import dataclass, field

from storage_manager.clients.gcs_client import GCSClient


# Fields that map directly to Video DB columns
VIDEO_COMMON_FIELDS = {"video_id", "fps", "height", "width"}

# Fields that map directly to Clip DB columns
CLIP_COMMON_FIELDS = {"video_id", "uri", "clip_start_time", "clip_end_time", "clip_duration"}


@dataclass
class ParsedVideo:
    video_id: str
    fps: float | None = None
    height: int | None = None
    width: int | None = None
    extra_metadata: dict = field(default_factory=dict)


@dataclass
class ParsedClip:
    video_id: str
    uri: str
    clip_start_time: float
    clip_end_time: float
    clip_duration: float
    extra_metadata: dict = field(default_factory=dict)


@dataclass
class IngestResult:
    videos: list[ParsedVideo]
    clips: list[ParsedClip]


def _parse_number(value: str | int | float | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _parse_int(value: str | int | float | None) -> int | None:
    n = _parse_number(value)
    return int(n) if n is not None else None


def _parse_video_row(row: dict) -> ParsedVideo:
    extra = {k: v for k, v in row.items() if k not in VIDEO_COMMON_FIELDS}
    return ParsedVideo(
        video_id=row["video_id"],
        fps=_parse_number(row.get("fps")),
        height=_parse_int(row.get("height")),
        width=_parse_int(row.get("width")),
        extra_metadata=extra if extra else {},
    )


def _parse_clip_row(row: dict) -> ParsedClip:
    extra = {k: v for k, v in row.items() if k not in CLIP_COMMON_FIELDS}
    return ParsedClip(
        video_id=row["video_id"],
        uri=row["uri"],
        clip_start_time=float(row["clip_start_time"]),
        clip_end_time=float(row["clip_end_time"]),
        clip_duration=float(row["clip_duration"]),
        extra_metadata=extra if extra else {},
    )


def _read_jsonl(gcs: GCSClient, blob_path: str) -> list[dict]:
    text = gcs.download_as_string(blob_path)
    rows = []
    for line in text.strip().splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def _find_metadata_file(gcs: GCSClient, prefix: str, filename: str) -> str | None:
    """Find a metadata file under the given prefix (searches one level deep)."""
    # Try direct path first
    direct = f"{prefix}{filename}"
    if gcs.blob_exists(direct):
        return direct

    # Search blobs under prefix for the filename
    blobs = gcs.list_blobs(prefix=prefix)
    for blob in blobs:
        if blob.name.endswith(filename):
            return blob.name

    return None


def ingest_from_gcs(bucket_name: str, prefix: str) -> IngestResult:
    """Read clip and video metadata JSONL files from a GCS bucket prefix.

    Args:
        bucket_name: GCS bucket name (e.g. "product-onsite")
        prefix: Path prefix within the bucket (e.g. "sample2/")

    Returns:
        IngestResult with parsed videos and clips.

    Raises:
        FileNotFoundError: If metadata files cannot be found.
    """
    gcs = GCSClient(bucket_name=bucket_name)

    # Normalize prefix
    if prefix and not prefix.endswith("/"):
        prefix += "/"

    clip_path = _find_metadata_file(gcs, prefix, "clip_metadata.jsonl")
    video_path = _find_metadata_file(gcs, prefix, "video_metadata.jsonl")

    if not clip_path:
        raise FileNotFoundError(f"clip_metadata.jsonl not found under gs://{bucket_name}/{prefix}")
    if not video_path:
        raise FileNotFoundError(f"video_metadata.jsonl not found under gs://{bucket_name}/{prefix}")

    video_rows = _read_jsonl(gcs, video_path)
    clip_rows = _read_jsonl(gcs, clip_path)

    videos = [_parse_video_row(row) for row in video_rows]
    clips = [_parse_clip_row(row) for row in clip_rows]

    return IngestResult(videos=videos, clips=clips)
