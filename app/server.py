"""Minimal content-platform API for a Kubernetes deployment exercise."""
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
        if path == "/healthz":
            status, payload = 200, {"status": "ok"}
        elif path == "/api/info":
            status, payload = 200, {
                "service": "content-api",
                "environment": ENVIRONMENT,
                "instance": socket.gethostname(),
            }
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
