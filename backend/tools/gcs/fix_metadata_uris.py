"""Fix clip_metadata.jsonl URIs to point to real GCS blobs.

Reads the existing metadata from the bucket, resolves each clip's URI
to a real blob path by matching on video_id, and writes the corrected
file back. All non-URI fields are preserved exactly as-is.

Usage (run inside the gateway container):
    python tools/gcs/fix_metadata_uris.py [--prefix sample2/] [--dry-run]
"""

import argparse
import json
import sys

from storage_manager.clients.gcs_client import GCSClient


BUCKET_NAME = "product-onsite"


def video_id_from_blob_name(blob_name: str) -> str:
    """Extract video_id from a blob path like 'sample2/clips/VIDEOID_HASH.mp4'."""
    filename = blob_name.rsplit("/", 1)[-1]
    name = filename.rsplit(".", 1)[0]
    parts = name.rsplit("_", 1)
    return parts[0] if len(parts) == 2 else name


def video_id_from_uri(uri: str) -> str:
    """Extract video_id from a gs:// URI."""
    # gs://bucket/prefix/clips/VIDEOID_HASH.mp4 -> VIDEOID
    path = uri.split("/")[-1]  # filename
    name = path.rsplit(".", 1)[0]
    parts = name.rsplit("_", 1)
    return parts[0] if len(parts) == 2 else name


def main():
    parser = argparse.ArgumentParser(description="Fix clip metadata URIs to point to real GCS blobs")
    parser.add_argument("--prefix", default="sample2/", help="Bucket prefix (default: sample2/)")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without uploading")
    args = parser.parse_args()

    prefix = args.prefix.rstrip("/") + "/"
    gcs = GCSClient(bucket_name=BUCKET_NAME)

    # 1. Build a map of video_id -> real blob gs:// URI
    print(f"Listing blobs under gs://{BUCKET_NAME}/{prefix}clips/ ...", file=sys.stderr)
    blobs = gcs.list_blobs(prefix=f"{prefix}clips/")
    video_blobs = [b for b in blobs if b.name.endswith((".mp4", ".webm", ".mov"))]
    print(f"  Found {len(video_blobs)} video files", file=sys.stderr)

    # Map video_id -> first matching blob URI
    real_uri_by_video_id: dict[str, str] = {}
    for blob in video_blobs:
        vid = video_id_from_blob_name(blob.name)
        if vid not in real_uri_by_video_id:
            real_uri_by_video_id[vid] = f"gs://{BUCKET_NAME}/{blob.name}"

    print(f"  {len(real_uri_by_video_id)} unique video_ids mapped", file=sys.stderr)

    # 2. Read existing clip metadata
    clip_path = f"{prefix}clip_metadata.jsonl"
    print(f"\nReading gs://{BUCKET_NAME}/{clip_path} ...", file=sys.stderr)
    text = gcs.download_as_string(clip_path)
    lines = text.strip().splitlines()
    print(f"  {len(lines)} clips in metadata", file=sys.stderr)

    # 3. Fix URIs
    fixed_clips = []
    fixed_count = 0
    skipped_count = 0

    for line in lines:
        clip = json.loads(line)
        old_uri = clip["uri"]
        vid = video_id_from_uri(old_uri)

        if vid in real_uri_by_video_id:
            new_uri = real_uri_by_video_id[vid]
            if old_uri != new_uri:
                clip["uri"] = new_uri
                fixed_count += 1
            fixed_clips.append(clip)
        else:
            print(f"  WARNING: no blob found for video_id={vid}, keeping original URI", file=sys.stderr)
            fixed_clips.append(clip)
            skipped_count += 1

    print(f"\n  {fixed_count} URIs fixed", file=sys.stderr)
    print(f"  {len(fixed_clips) - fixed_count - skipped_count} already correct", file=sys.stderr)
    if skipped_count:
        print(f"  {skipped_count} skipped (no matching blob)", file=sys.stderr)

    # 4. Verify a sample
    print("\nSample (first 3 clips):", file=sys.stderr)
    for clip in fixed_clips[:3]:
        blob_path = clip["uri"].removeprefix(f"gs://{BUCKET_NAME}/")
        exists = gcs.blob_exists(blob_path)
        status = "OK" if exists else "MISSING"
        print(f"  [{status}] {clip['uri']}", file=sys.stderr)

    if args.dry_run:
        print("\n--dry-run: not uploading. First 2 clips:", file=sys.stderr)
        for clip in fixed_clips[:2]:
            print(json.dumps(clip), file=sys.stderr)
        return

    # 5. Upload corrected metadata
    new_content = "\n".join(json.dumps(c) for c in fixed_clips) + "\n"
    print(f"\nUploading corrected metadata to gs://{BUCKET_NAME}/{clip_path} ...", file=sys.stderr)
    gcs.upload_from_string(clip_path, new_content, content_type="application/jsonl")
    print("Done.", file=sys.stderr)


if __name__ == "__main__":
    main()
