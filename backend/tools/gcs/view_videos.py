"""Serve bucket videos in a local browser viewer with signed URLs, paginated."""

import datetime
import http.server
import json
import sys
import threading
import webbrowser
from urllib.parse import parse_qs, urlparse

from google.cloud import storage


BUCKET_NAME = "product-onsite"
PORT = 8888
PAGE_SIZE = 5
SIGNED_URL_EXPIRATION = datetime.timedelta(hours=2)


def get_video_blobs(prefix: str | None = None) -> list[storage.Blob]:
    client = storage.Client()
    blobs = client.list_blobs(BUCKET_NAME, prefix=prefix)
    return [b for b in blobs if b.name.endswith((".mp4", ".webm", ".mov"))]


def sign_page(blobs: list[storage.Blob], page: int) -> list[dict]:
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    videos = []
    for blob in blobs[start:end]:
        url = blob.generate_signed_url(expiration=SIGNED_URL_EXPIRATION)
        videos.append({
            "name": blob.name,
            "url": url,
            "size_mb": round(blob.size / (1024 * 1024), 2) if blob.size else 0,
        })
    return videos


HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>GCS Video Viewer - {bucket}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: system-ui, sans-serif; background: #111; color: #eee; padding: 20px; }}
        h1 {{ margin-bottom: 16px; font-size: 18px; color: #aaa; }}
        .video-list {{ display: flex; flex-direction: column; gap: 24px; max-width: 960px; margin: 0 auto; }}
        .video-card {{ background: #1a1a1a; border-radius: 8px; overflow: hidden; }}
        .video-card video {{ width: 100%; display: block; }}
        .video-info {{ padding: 12px 16px; font-size: 13px; color: #999; display: flex; justify-content: space-between; }}
        .video-name {{ color: #ccc; font-weight: 500; }}
        .pagination {{ display: flex; justify-content: center; gap: 12px; margin: 24px auto; max-width: 960px; }}
        .pagination a {{
            padding: 8px 20px; border-radius: 6px; background: #222; color: #ccc;
            text-decoration: none; font-size: 14px;
        }}
        .pagination a:hover {{ background: #333; }}
        .pagination .disabled {{ opacity: 0.3; pointer-events: none; }}
        .page-info {{ color: #666; font-size: 13px; align-self: center; }}
    </style>
</head>
<body>
    <h1>gs://{bucket}/ &mdash; {total} videos</h1>
    <div class="video-list" id="list"></div>
    <div class="pagination">
        <a href="/?page={prev_page}" class="{prev_disabled}">&larr; Prev</a>
        <span class="page-info">Page {display_page} of {total_pages}</span>
        <a href="/?page={next_page}" class="{next_disabled}">Next &rarr;</a>
    </div>
    <script>
        const videos = {video_json};
        const list = document.getElementById('list');
        videos.forEach(v => {{
            const card = document.createElement('div');
            card.className = 'video-card';
            card.innerHTML = `
                <video controls preload="metadata" src="${{v.url}}"></video>
                <div class="video-info">
                    <span class="video-name">${{v.name}}</span>
                    <span>${{v.size_mb}} MB</span>
                </div>
            `;
            list.appendChild(card);
        }});
    </script>
</body>
</html>"""


all_blobs: list[storage.Blob] = []


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        page = int(qs.get("page", ["0"])[0])
        page = max(0, page)

        total = len(all_blobs)
        total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        page = min(page, total_pages - 1)

        videos = sign_page(all_blobs, page)

        html = HTML_TEMPLATE.format(
            bucket=BUCKET_NAME,
            total=total,
            video_json=json.dumps(videos),
            prev_page=page - 1,
            next_page=page + 1,
            display_page=page + 1,
            total_pages=total_pages,
            prev_disabled="disabled" if page == 0 else "",
            next_disabled="disabled" if page >= total_pages - 1 else "",
        )

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        pass


def main(prefix: str | None = None):
    global all_blobs

    print(f"Listing videos in gs://{BUCKET_NAME}/{prefix or ''}...")
    all_blobs = get_video_blobs(prefix)

    if not all_blobs:
        print("No video files found.")
        sys.exit(1)

    total_pages = (len(all_blobs) + PAGE_SIZE - 1) // PAGE_SIZE
    print(f"Found {len(all_blobs)} videos ({total_pages} pages of {PAGE_SIZE}). Starting server on http://localhost:{PORT}")

    server = http.server.HTTPServer(("localhost", PORT), Handler)
    threading.Thread(target=lambda: webbrowser.open(f"http://localhost:{PORT}"), daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()


if __name__ == "__main__":
    prefix = sys.argv[1] if len(sys.argv) > 1 else None
    main(prefix)
