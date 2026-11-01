"""Second release of the content platform API; no third-party packages required."""
import json
import os
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

PORT = int(os.environ.get("PORT", "8080"))
ENVIRONMENT = os.environ.get("APP_ENV", "unset")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        if path in ("/healthz", "/readyz"):
            status, payload = 200, {"status": "ok"}
        elif path == "/api/info":
            status, payload = 200, {
                "service": "content-api",
                "environment": ENVIRONMENT,
                "instance": socket.gethostname(),
                "version": "v2",
            }
        elif path == "/api/features":
            status, payload = 200, {
                "features": ["content-calendar", "drafts"],
                "version": "v2",
            }
        elif path.startswith("/api/features/"):
            feature_name = path.removeprefix("/api/features/")
            features = {
                "content-calendar": {
                    "name": "content-calendar",
                    "description": "Plan and organize scheduled content.",
                },
                "drafts": {
                    "name": "drafts",
                    "description": "Save content before it is published.",
                },
            }
            if feature_name in features:
                status, payload = 200, {**features[feature_name], "version": "v2"}
            else:
                status, payload = 404, {"error": "not found"}
        else:
            status, payload = 404, {"error": "not found"}
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
