"""Download the OpenAPI spec from the running gateway."""

import json
import time
from pathlib import Path

import requests

GATEWAY_URL = "http://localhost:1301"
OUTPUT_PATH = Path(__file__).parent / "generated" / "openapi.json"


def main():
    while True:
        try:
            r = requests.get(f"{GATEWAY_URL}/openapi.json")
            r.raise_for_status()
            break
        except Exception:
            print("Waiting for API...")
            time.sleep(2)
            continue

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(r.json(), f, indent=4)

    print(f"OpenAPI spec saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
