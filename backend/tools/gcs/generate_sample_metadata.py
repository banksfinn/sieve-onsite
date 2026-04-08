"""Generate sample clip and video metadata from videos in the GCS bucket.

Queries the bucket for video files, randomly samples clips from them,
and outputs JSON matching the format expected by the dataset version API.

Usage:
    python generate_sample_metadata.py [--prefix PREFIX] [--samples N] [--output FILE]
"""

import argparse
import json
import random
import sys

from google.cloud import storage


BUCKET_NAME = "product-onsite"

# Realistic defaults for generated metadata
FPS_OPTIONS = [23.976, 24.0, 25.0, 29.97, 30.0, 59.94, 60.0]
RESOLUTION_OPTIONS = [(1920, 1080), (1280, 720), (3840, 2160), (2560, 1440)]
SOURCE_OPTIONS = ["web", "visora", "upload", "studio"]
LANGUAGE_OPTIONS = ["en", "es", "fr", "de", "ja", "ko", "zh", "pt", "fa", "ar"]

# Clip generation parameters
MIN_CLIP_DURATION = 2.0
MAX_CLIP_DURATION = 15.0
ASSUMED_VIDEO_DURATION = 120.0  # assume 2min if we can't determine length


def get_video_blobs(prefix: str | None = None) -> list[storage.Blob]:
    client = storage.Client()
    blobs = client.list_blobs(BUCKET_NAME, prefix=prefix)
    return [b for b in blobs if b.name.endswith((".mp4", ".webm", ".mov"))]


def delivery_id_from_blob(blob: storage.Blob) -> str:
    """Extract a delivery_id from the blob name (filename without extension)."""
    name = blob.name.rsplit("/", 1)[-1]
    return name.rsplit(".", 1)[0]


def generate_clips_for_video(
    delivery_id: str, num_clips: int, bucket_name: str = BUCKET_NAME
) -> list[dict]:
    """Generate random clip metadata entries for a single video."""
    clips = []
    cursor = 0.0

    for i in range(num_clips):
        gap = round(random.uniform(1.0, 20.0), 2)
        start = round(cursor + gap, 2)
        duration = round(random.uniform(MIN_CLIP_DURATION, MAX_CLIP_DURATION), 2)
        end = round(start + duration, 2)

        clip = {
            "delivery_id": delivery_id,
            "uri": f"gs://{bucket_name}/videos/{delivery_id}_clip_{i + 1}.mp4",
            "clip_start_time": start,
            "clip_end_time": end,
            "clip_duration": duration,
            "avg_face_size": random.randint(50, 200),
            "max_num_faces": random.randint(0, 5),
            "is_full_body": random.choice([True, False]),
            "has_overlay": random.choice([True, False]),
        }
        clips.append(clip)
        cursor = end

    return clips


def generate_video_metadata(delivery_id: str) -> dict:
    """Generate random video-level metadata for a delivery_id."""
    width, height = random.choice(RESOLUTION_OPTIONS)
    return {
        "delivery_id": delivery_id,
        "fps": random.choice(FPS_OPTIONS),
        "height": height,
        "width": width,
        "source": random.choice(SOURCE_OPTIONS),
        "language": random.choice(LANGUAGE_OPTIONS),
    }


def main():
    parser = argparse.ArgumentParser(description="Generate sample clip metadata from GCS videos")
    parser.add_argument("--prefix", default=None, help="GCS prefix to filter videos")
    parser.add_argument("--samples", type=int, default=None, help="Number of clips to generate (spread across videos)")
    parser.add_argument("--output", default=None, help="Output file path (default: stdout)")
    parser.add_argument("--clips-per-video", type=int, default=None, help="Clips per video (overrides --samples)")
    args = parser.parse_args()

    print(f"Listing videos in gs://{BUCKET_NAME}/{args.prefix or ''}...", file=sys.stderr)
    blobs = get_video_blobs(args.prefix)

    if not blobs:
        print("No video files found in bucket.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(blobs)} videos.", file=sys.stderr)

    # Determine sample count
    total_samples = args.samples
    if total_samples is None:
        try:
            total_samples = int(input(f"How many sample clips to generate? [{len(blobs) * 2}]: ").strip() or len(blobs) * 2)
        except (EOFError, KeyboardInterrupt):
            total_samples = len(blobs) * 2
            print(f"\nUsing default: {total_samples}", file=sys.stderr)

    # Distribute clips across videos
    delivery_ids = []
    for blob in blobs:
        did = delivery_id_from_blob(blob)
        delivery_ids.append(did)

    if args.clips_per_video is not None:
        clips_per = {did: args.clips_per_video for did in delivery_ids}
    else:
        # Spread samples across videos, at least 1 per video
        base = max(1, total_samples // len(delivery_ids))
        remainder = total_samples - base * len(delivery_ids)
        clips_per = {did: base for did in delivery_ids}
        for did in random.sample(delivery_ids, min(abs(remainder), len(delivery_ids))):
            clips_per[did] += 1 if remainder > 0 else 0

    # Generate metadata
    all_clips = []
    all_videos = []

    for did in delivery_ids:
        all_videos.append(generate_video_metadata(did))
        all_clips.extend(generate_clips_for_video(did, clips_per[did]))

    output = {
        "clips": all_clips,
        "videos": all_videos,
    }

    result = json.dumps(output, indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(result)
        print(f"Wrote {len(all_clips)} clips and {len(all_videos)} videos to {args.output}", file=sys.stderr)
    else:
        print(result)

    print(f"\nGenerated {len(all_clips)} clips across {len(all_videos)} videos.", file=sys.stderr)


if __name__ == "__main__":
    main()
