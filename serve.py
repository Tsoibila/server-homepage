#!/usr/bin/env python3
"""
Static file server for ~/homepage + a small /list/<folder> API.

Endpoints:
    /                          static files (index.html, etc.)
    /list/Images               {"files": [...]}   media files
    /list/random-songs         {"files": [...]}   audio files
    /images.json               legacy alias for /list/Images
    /songs.json                legacy alias for /list/random-songs

Run:
    python3 serve.py
"""
import json
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE = Path(__file__).resolve().parent

MEDIA_EXTS = {
    ".gif", ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".svg", ".avif",
    ".mp4", ".webm", ".ogv", ".mov", ".m4v",
}
AUDIO_EXTS = {".mp3", ".ogg", ".wav", ".m4a", ".flac"}

# Folders the API is allowed to enumerate.
LISTABLE = {
    "Images":       MEDIA_EXTS,
    "random-songs": AUDIO_EXTS,
}

# Bind address / port. Change BIND_HOST to your LAN IP if you want to reach
# the console from another device on your network (e.g. "192.168.1.50").
BIND_HOST = "0.0.0.0"
BIND_PORT = 8000


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(BASE), **kw)

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------
    def do_GET(self):
        path = self.path.split("?", 1)[0]

        if path.startswith("/list/"):
            folder = urllib.parse.unquote(path[len("/list/"):]).strip("/")
            return self._list_folder(folder)

        if path == "/songs.json":
            return self._list_folder("random-songs", key="songs")
        if path == "/images.json":
            return self._list_folder("Images", key="images")

        return super().do_GET()

    # ------------------------------------------------------------------
    # /list/<folder> implementation
    # ------------------------------------------------------------------
    def _list_folder(self, folder_name, key="files"):
        exts = LISTABLE.get(folder_name)
        if exts is None:
            return self._json({"error": f"folder not listable: {folder_name}"}, 403)

        folder = (BASE / folder_name).resolve()
        # Must stay inside BASE (blocks ../ traversal).
        if not folder.is_relative_to(BASE):
            return self._json({"error": "invalid path"}, 403)

        files = []
        if folder.is_dir():
            for f in sorted(folder.iterdir()):
                if f.is_file() and f.suffix.lower() in exts:
                    files.append(f.name)

        return self._json({key: files})

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        self.wfile.write(body)

    def _err(self, code, msg):
        body = msg.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *a):
        msg = fmt % a
        if "/list/" in msg or ".json" in msg:
            print("API:", msg)
        else:
            super().log_message(fmt, *a)


if __name__ == "__main__":
    print(f"Server:  http://{BIND_HOST}:{BIND_PORT}/")
    print(f"         http://{BIND_HOST}:{BIND_PORT}/list/Images")
    print(f"         http://{BIND_HOST}:{BIND_PORT}/list/random-songs")
    ThreadingHTTPServer((BIND_HOST, BIND_PORT), Handler).serve_forever()
