"""Generate sample clip and video metadata from videos in the GCS bucket.

Queries the bucket for video files, randomly samples them, and outputs
JSONL files matching the format used by sample2/ in the product-onsite bucket.

Usage:
    python generate_sample_metadata.py [--prefix PREFIX] [--samples N] [--output-dir DIR]
"""

import argparse
import json
import random
import sys

from google.cloud import storage


BUCKET_NAME = "product-onsite"

# Video metadata options
FPS_OPTIONS = [24, 25, 29.97, 30, 30.03003, 60]
RESOLUTION_OPTIONS = [(1920, 1080), (1280, 720), (3840, 2160), (2560, 1440)]

# Clip generation parameters
MIN_CLIP_DURATION = 3
MAX_CLIP_DURATION = 420


def get_video_blobs(prefix: str | None = None) -> list:
    client = storage.Client()
    blobs = client.list_blobs(BUCKET_NAME, prefix=prefix)
    return [b for b in blobs if b.name.endswith((".mp4", ".webm", ".mov"))]


def video_id_from_blob(blob) -> str:
    """Extract video_id from blob name: takes the first segment before the last underscore+hash."""
    filename = blob.name.rsplit("/", 1)[-1]
    name = filename.rsplit(".", 1)[0]
    # Clip filenames are {video_id}_{hash}.mp4 — split on the last underscore
    parts = name.rsplit("_", 1)
    return parts[0] if len(parts) == 2 else name


def random_fraction() -> float:
    """Generate a random fraction, biased toward 0 and 1."""
    r = random.random()
    if r < 0.4:
        return 0.0
    if r < 0.7:
        return 1.0
    return round(random.random(), 8)


def generate_clip(video_id: str, clip_uri: str, start: int, duration: int) -> dict:
    return {
        "video_id": video_id,
        "uri": clip_uri,
        "clip_start_time": str(start),
        "clip_end_time": str(start + duration),
        "clip_duration": duration,
        "one_hand_presence_fraction": str(random_fraction()),
        "two_hands_presence_fraction": random_fraction(),
        "phone_screen_presence_fraction": str(random_fraction()),
        "pc_screen_presence_fraction": str(random_fraction()),
        "other_screen_presence_fraction": str(random_fraction()),
        "is_egocentric_fraction": str(random_fraction()),
        "waist_visible_fraction": random_fraction(),
        "well_lit_fraction": str(random_fraction()),
        "has_overlay_fraction": str(random_fraction()),
    }


def generate_clips_for_video(video_id: str, num_clips: int, sample_prefix: str) -> list[dict]:
    clips = []
    cursor = 0

    for _ in range(num_clips):
        gap = random.randint(1, 60)
        start = cursor + gap
        duration = random.randint(MIN_CLIP_DURATION, MAX_CLIP_DURATION)
        clip_hash = f"{random.getrandbits(64):016x}"
        uri = f"gs://{BUCKET_NAME}/{sample_prefix}clips/{video_id}_{clip_hash}.mp4"

        clips.append(generate_clip(video_id, uri, start, duration))
        cursor = start + duration

    return clips


def generate_video_metadata(video_id: str) -> dict:
    width, height = random.choice(RESOLUTION_OPTIONS)
    return {
        "width": str(width),
        "height": str(height),
        "fps": random.choice(FPS_OPTIONS),
        "has_black_bars": random.choice([True, False]),
        "is_upright": random.choice([True, True, True, False]),  # mostly upright
        "video_id": video_id,
    }


def main():
    parser = argparse.ArgumentParser(description="Generate sample clip metadata from GCS videos")
    parser.add_argument("--prefix", default=None, help="GCS prefix to filter videos (e.g. sample2/clips/)")
    parser.add_argument("--samples", type=int, default=None, help="Total number of clips to generate")
    parser.add_argument("--clips-per-video", type=int, default=None, help="Clips per video (overrides --samples)")
    parser.add_argument("--output-dir", default=None, help="Output directory for JSONL files (default: stdout)")
    args = parser.parse_args()

    print(f"Listing videos in gs://{BUCKET_NAME}/{args.prefix or ''}...", file=sys.stderr)
    blobs = get_video_blobs(args.prefix)

    if not blobs:
        print("No video files found in bucket.", file=sys.stderr)
        sys.exit(1)

    # Deduplicate by video_id
    video_ids = list({video_id_from_blob(b) for b in blobs})
    video_ids.sort()
    print(f"Found {len(blobs)} clips across {len(video_ids)} unique videos.", file=sys.stderr)

    # Determine sample count
    total_samples = args.samples
    if total_samples is None and args.clips_per_video is None:
        default = len(video_ids) * 2
        try:
            total_samples = int(input(f"How many sample clips to generate? [{default}]: ").strip() or default)
        except (EOFError, KeyboardInterrupt):
            total_samples = default
            print(f"\nUsing default: {total_samples}", file=sys.stderr)

    # Figure out the sample prefix for URIs
    sample_prefix = ""
    if args.prefix:
        # e.g. "sample2/clips/" -> "sample2/"
        parts = args.prefix.rstrip("/").split("/")
        if len(parts) > 1:
            sample_prefix = "/".join(parts[:-1]) + "/"
        else:
            sample_prefix = parts[0] + "/"

    # Distribute clips across videos
    if args.clips_per_video is not None:
        clips_per = {vid: args.clips_per_video for vid in video_ids}
    else:
        base = max(1, total_samples // len(video_ids))
        remainder = total_samples - base * len(video_ids)
        clips_per = {vid: base for vid in video_ids}
        extras = random.sample(video_ids, min(abs(remainder), len(video_ids)))
        for vid in extras:
            clips_per[vid] += 1 if remainder > 0 else 0

    # Generate metadata
    all_clips = []
    all_videos = []

    for vid in video_ids:
        all_videos.append(generate_video_metadata(vid))
        all_clips.extend(generate_clips_for_video(vid, clips_per[vid], sample_prefix))

    clip_lines = [json.dumps(c) for c in all_clips]
    video_lines = [json.dumps(v) for v in all_videos]

    if args.output_dir:
        import os
        os.makedirs(args.output_dir, exist_ok=True)

        clip_path = os.path.join(args.output_dir, "clip_metadata.jsonl")
        video_path = os.path.join(args.output_dir, "video_metadata.jsonl")

        with open(clip_path, "w") as f:
            f.write("\n".join(clip_lines) + "\n")
        with open(video_path, "w") as f:
            f.write("\n".join(video_lines) + "\n")

        print(f"Wrote {len(all_clips)} clips to {clip_path}", file=sys.stderr)
        print(f"Wrote {len(all_videos)} videos to {video_path}", file=sys.stderr)
    else:
        print("=== clip_metadata.jsonl ===")
        for line in clip_lines:
            print(line)
        print("\n=== video_metadata.jsonl ===")
        for line in video_lines:
            print(line)

    print(f"\nGenerated {len(all_clips)} clips across {len(all_videos)} videos.", file=sys.stderr)


if __name__ == "__main__":
    main()
