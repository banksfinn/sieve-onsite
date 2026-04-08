"""List contents of the GCS bucket."""

import sys

from google.cloud import storage


BUCKET_NAME = "product-onsite"


def main(prefix: str | None = None):
    client = storage.Client()
    blobs = client.list_blobs(BUCKET_NAME, prefix=prefix)

    count = 0
    for blob in blobs:
        size_mb = blob.size / (1024 * 1024) if blob.size else 0
        print(f"  {blob.name:80s} {size_mb:>8.2f} MB")
        count += 1

    print(f"\n{count} objects found")


if __name__ == "__main__":
    prefix = sys.argv[1] if len(sys.argv) > 1 else None
    main(prefix)
