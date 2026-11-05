import os
import sys
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, HTTPServer

PROJECT_ROOT = Path(__file__).resolve().parent
DIST_DIR = PROJECT_ROOT / "frontend" / "dist"

class SPAServerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST_DIR), **kwargs)

    def do_GET(self):
        path = self.translate_path(self.path)
        if not os.path.exists(path) or os.path.isdir(path):
            self.path = '/index.html'
        return super().do_GET()

if __name__ == "__main__":
    print("Serving PRAVAHA frontend at http://localhost:5173")
    server = HTTPServer(('127.0.0.1', 5173), SPAServerHandler)
    server.serve_forever()

