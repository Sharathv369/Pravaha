"""
PRAVAHA — Unified Platform Launcher
Starts the FastAPI hydrologic backend (port 8000) and the SPA frontend server (port 5173).
"""

import os
import sys
import time
import socket
import threading
import subprocess
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

def start_backend():
    python_exe = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
    print(f"[*] Starting PRAVAHA FastAPI Backend on http://127.0.0.1:8000...")
    for attempt in range(5):
        proc = subprocess.Popen([
            str(python_exe),
            "-m",
            "uvicorn",
            "src.api.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
            "--log-level",
            "info"
        ], cwd=str(PROJECT_ROOT))
        time.sleep(2)
        if proc.poll() is None:
            print(">>> FastAPI Backend running successfully on http://127.0.0.1:8000")
            proc.wait()
            break
        print(f"[*] Port 8000 in TIME_WAIT, retrying in 2s (attempt {attempt+1}/5)...")
        time.sleep(2)

def start_frontend():
    print(f"[*] Starting PRAVAHA Frontend Interface on http://localhost:5173...")
    server = HTTPServer(('127.0.0.1', 5173), SPAServerHandler)
    print(">>> Frontend Interface running successfully on http://localhost:5173")
    server.serve_forever()

if __name__ == "__main__":
    t_back = threading.Thread(target=start_backend, daemon=True)
    t_back.start()
    time.sleep(2)
    start_frontend()
