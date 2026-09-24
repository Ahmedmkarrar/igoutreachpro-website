#!/usr/bin/env python3
"""Local preview that mimics Vercel's cleanUrls and 404.html.  python3 tools/serve.py [port]"""
import http.server
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def send_head(self):
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        local = ROOT / path.lstrip("/")
        if path != "/" and local.is_dir() and (local / "index.html").exists():
            self.path = path.rstrip("/") + "/index.html"
        elif path != "/" and not local.exists() and (ROOT / (path.lstrip("/").rstrip("/") + ".html")).exists():
            self.path = path.rstrip("/") + ".html"
        elif path != "/" and not local.exists():
            self.send_response(404)
            body = (ROOT / "404.html").read_bytes()
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return None
        return super().send_head()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8477
    os.chdir(ROOT)
    http.server.ThreadingHTTPServer(("", port), Handler).serve_forever()
