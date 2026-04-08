"""Fix clip_metadata.jsonl durations using ffprobe against real GCS files.

Phase 1: Probes real durations in parallel, generates random start times,
         and writes corrected metadata to a local file for review.
         Supports --skip to resume after a timeout.
Phase 2: Uploads the reviewed file to GCS.

Usage (run from backend/):
    # Phase 1: probe and write local file (first run)
    GOOGLE_APPLICATION_CREDENTIALS=../secrets/gcs-service-account.json \
        uv run python tools/gcs/fix_metadata_durations.py --prefix sample2/ --output durations.jsonl

    # Phase 1: resume after timeout (appends to existing file)
    GOOGLE_APPLICATION_CREDENTIALS=../secrets/gcs-service-account.json \
        uv run python tools/gcs/fix_metadata_durations.py --prefix sample2/ --output durations.jsonl --skip 214

    # Phase 2: apply durations to clip metadata and upload
    GOOGLE_APPLICATION_CREDENTIALS=../secrets/gcs-service-account.json \
        uv run python tools/gcs/fix_metadata_durations.py --upload durations.jsonl --prefix sample2/
"""

import argparse
import datetime
import json
import random
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from google.cloud import storage


BUCKET_NAME = "product-onsite"
SIGNED_URL_EXPIRATION = datetime.timedelta(hours=1)
MAX_WORKERS = 10


def probe_duration(signed_url: str) -> float | None:
    """Use ffprobe to get the duration of a video at a signed URL."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                signed_url,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        return None
    if result.returncode != 0:
        return None
    try:
        info = json.loads(result.stdout)
        return float(info["format"]["duration"])
    except (KeyError, ValueError, json.JSONDecodeError):
        return None


def probe_uri(uri: str, bucket) -> tuple[str, float | None]:
    """Probe a single URI. Returns (uri, duration)."""
    blob_path = uri.removeprefix(f"gs://{BUCKET_NAME}/")
    b = bucket.blob(blob_path)
    signed_url = b.generate_signed_url(expiration=SIGNED_URL_EXPIRATION)
    duration = probe_duration(signed_url)
    return uri, duration


def random_start_time(duration: float) -> float:
    """Generate a plausible random start time within a longer source video."""
    # Assume source videos are 1-10 minutes long
    max_source = random.uniform(max(duration * 2, 60), 600)
    max_start = max_source - duration
    return round(random.uniform(0, max_start), 2)


def phase_probe(prefix: str, output_path: str, skip: int = 0):
    """Phase 1: probe durations and write a URI->duration lookup file.

    Output format is one JSON object per line: {"uri": "...", "duration": 5.07}
    Appends to the file so it can be resumed with --skip.
    """
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    # 1. Read existing clip metadata to get unique URIs
    clip_blob_path = f"{prefix}clip_metadata.jsonl"
    print(f"Reading gs://{BUCKET_NAME}/{clip_blob_path} ...", file=sys.stderr)
    blob = bucket.blob(clip_blob_path)
    text = blob.download_as_text()
    clips = [json.loads(line) for line in text.strip().splitlines() if line.strip()]
    print(f"  {len(clips)} clips in metadata", file=sys.stderr)

    unique_uris = sorted({clip["uri"] for clip in clips})
    total = len(unique_uris)
    print(f"  {total} unique URIs total", file=sys.stderr)

    # 2. Skip already-probed URIs
    uris_to_probe = unique_uris[skip:]
    if skip:
        print(f"  Skipping first {skip}, probing {len(uris_to_probe)} remaining", file=sys.stderr)

    # 3. Probe in parallel, appending results as they come
    print(f"  Probing with {MAX_WORKERS} workers ...", file=sys.stderr)
    completed = 0
    interrupted = False

    with open(output_path, "a") as f:
        pool = ThreadPoolExecutor(max_workers=MAX_WORKERS)
        futures = {pool.submit(probe_uri, uri, bucket): uri for uri in uris_to_probe}
        try:
            for future in as_completed(futures):
                uri, duration = future.result()
                completed += 1

                record = {"uri": uri, "duration": duration}
                f.write(json.dumps(record) + "\n")
                f.flush()

                blob_path = uri.removeprefix(f"gs://{BUCKET_NAME}/")
                status = f"{duration:.2f}s" if duration is not None else "FAILED"
                print(f"  [{skip + completed}/{total}] {blob_path} -> {status}", file=sys.stderr)
        except KeyboardInterrupt:
            interrupted = True
            print("\n\nInterrupted! Cancelling pending work...", file=sys.stderr)
            for fut in futures:
                fut.cancel()
            pool.shutdown(wait=False, cancel_futures=True)

    print(f"\nAppended {completed} results to {output_path}", file=sys.stderr)
    next_skip = skip + completed
    remaining = total - next_skip
    if remaining > 0:
        print(f"  {remaining} still remaining. Resume with:", file=sys.stderr)
        print(f"  --output {output_path} --skip {next_skip}", file=sys.stderr)
    else:
        print("  All URIs probed. Run with --upload to apply.", file=sys.stderr)

    if interrupted:
        sys.exit(130)


def phase_upload(durations_path: str, prefix: str):
    """Phase 2: apply probed durations to clip metadata and upload."""
    # 1. Load duration lookup
    duration_by_uri: dict[str, float | None] = {}
    with open(durations_path) as f:
        for line in f:
            line = line.strip()
            if line:
                record = json.loads(line)
                duration_by_uri[record["uri"]] = record["duration"]

    print(f"Loaded {len(duration_by_uri)} duration records from {durations_path}", file=sys.stderr)

    # 2. Read existing clip metadata from GCS
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    clip_blob_path = f"{prefix}clip_metadata.jsonl"

    print(f"Reading gs://{BUCKET_NAME}/{clip_blob_path} ...", file=sys.stderr)
    blob = bucket.blob(clip_blob_path)
    text = blob.download_as_text()
    clips = [json.loads(line) for line in text.strip().splitlines() if line.strip()]
    print(f"  {len(clips)} clips in metadata", file=sys.stderr)

    # 3. Apply durations with random start times
    fixed_count = 0
    failed_count = 0
    missing_count = 0

    for clip in clips:
        uri = clip["uri"]
        if uri not in duration_by_uri:
            missing_count += 1
            continue

        real_duration = duration_by_uri[uri]
        if real_duration is None:
            failed_count += 1
            continue

        start = random_start_time(real_duration)
        clip["clip_start_time"] = str(start)
        clip["clip_end_time"] = str(round(start + real_duration, 2))
        clip["clip_duration"] = round(real_duration, 2)
        fixed_count += 1

    print(f"\n  {fixed_count} clips updated", file=sys.stderr)
    if failed_count:
        print(f"  {failed_count} failed probes (kept original)", file=sys.stderr)
    if missing_count:
        print(f"  {missing_count} URIs not in durations file (kept original)", file=sys.stderr)

    # 4. Show sample
    print("\nSample (first 3 clips):", file=sys.stderr)
    for clip in clips[:3]:
        print(f"  {clip['video_id']}: duration={clip['clip_duration']}, "
              f"start={clip['clip_start_time']}, end={clip['clip_end_time']}", file=sys.stderr)

    # 5. Upload
    new_content = "\n".join(json.dumps(c) for c in clips) + "\n"
    print(f"\nUploading to gs://{BUCKET_NAME}/{clip_blob_path} ...", file=sys.stderr)
    blob.upload_from_string(new_content, content_type="application/jsonl")
    print("Done.", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Fix clip metadata durations from real GCS files")
    parser.add_argument("--prefix", default="sample2/", help="Bucket prefix (default: sample2/)")
    parser.add_argument("--output", default=None, help="Phase 1: probe durations to this file")
    parser.add_argument("--skip", type=int, default=0, help="Phase 1: skip first N URIs (for resuming)")
    parser.add_argument("--upload", default=None, help="Phase 2: apply durations file and upload to GCS")
    args = parser.parse_args()

    prefix = args.prefix.rstrip("/") + "/"

    if args.upload:
        phase_upload(args.upload, prefix)
    elif args.output:
        phase_probe(prefix, args.output, skip=args.skip)
    else:
        parser.error("Specify --output FILE (phase 1) or --upload FILE (phase 2)")


if __name__ == "__main__":
    main()
