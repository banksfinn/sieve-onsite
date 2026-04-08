"""Download a single file from the GCS bucket."""

import sys
from pathlib import Path

from google.cloud import storage


BUCKET_NAME = "product-onsite"


def main(blob_path: str, output_dir: str = "downloads"):
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_path)

    if not blob.exists():
        print(f"Blob not found: {blob_path}")
        sys.exit(1)

    out = Path(output_dir) / Path(blob_path).name
    out.parent.mkdir(parents=True, exist_ok=True)

    blob.download_to_filename(str(out))
    size_mb = out.stat().st_size / (1024 * 1024)
    print(f"Downloaded {blob_path} -> {out} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_file.py <blob_path> [output_dir]")
        sys.exit(1)

    blob_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "downloads"
    main(blob_path, output_dir)
