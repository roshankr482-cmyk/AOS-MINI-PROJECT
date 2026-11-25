#!/usr/bin/env python3
"""KernelX server: serves the UI and exposes the C engine (libkernelx.so) as a JSON API.
Only Python standard library is used - no pip install needed."""
import argparse, ctypes, json, os, sys, threading, webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
IS_WIN = os.name == "nt"
LIB_PATH = os.path.join(ROOT, "backend", "kernelx.dll" if IS_WIN else "libkernelx.so")
FRONTEND = os.path.join(ROOT, "frontend")
sys.path.insert(0, ROOT)

ENGINE_NAME = "C (native)"
lib = None
if os.path.exists(LIB_PATH):
    try:
        if IS_WIN and hasattr(os, "add_dll_directory"):
            os.add_dll_directory(os.path.dirname(LIB_PATH))
        lib = ctypes.CDLL(LIB_PATH)
        lib.kernelx_run.restype = ctypes.c_void_p            # keep raw pointer so we can free it
        lib.kernelx_run.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int]
        lib.kernelx_free.argtypes = [ctypes.c_void_p]
        lib.kernelx_free.restype = None
    except OSError as e:
        print("[kernelx] Could not load C library (%s) - using Python engine." % e)
        lib = None
if lib is None:
    if not IS_WIN:
        sys.exit("libkernelx.so not found. Run:  cd backend && make   (or use ./run.sh)")
    import pyengine
    ENGINE_NAME = "Python (same algorithms, no C compiler found)"
LOCK = threading.Lock()

def run_c(alg, reqs, head, lo, hi, d):
    if lib is None:
        return pyengine.run(alg, reqs, head, lo, hi, d)
    with LOCK:
        ptr = lib.kernelx_run(alg, reqs.encode(), head, lo, hi, d)
        if not ptr:
            return {"error": "Engine returned no data"}
        try:
            return json.loads(ctypes.string_at(ptr).decode())
        finally:
            lib.kernelx_free(ptr)

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=FRONTEND, **kw)

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/health":
            return self._json({"ok": True, "engine": ENGINE_NAME})
        return super().do_GET()

    def do_POST(self):
        if self.path not in ("/api/run", "/api/compare"):
            return self._json({"error": "Not found"}, 404)
        try:
            n = int(self.headers.get("Content-Length", 0))
            if n <= 0 or n > 2_000_000:
                return self._json({"error": "Bad request size"}, 400)
            p = json.loads(self.rfile.read(n))
            reqs = str(p["req"])
            head, lo, hi, d = int(p["head"]), int(p["min"]), int(p["max"]), 1 if int(p.get("dir", 1)) else 0
            if self.path == "/api/run":
                return self._json(run_c(int(p["alg"]), reqs, head, lo, hi, d))
            return self._json([run_c(i, reqs, head, lo, hi, d) for i in range(6)])
        except (KeyError, ValueError, TypeError, json.JSONDecodeError):
            return self._json({"error": "Malformed request"}, 400)

    def log_message(self, fmt, *args):
        msg = fmt % args
        if "/api/" not in msg:
            sys.stderr.write("[kernelx] " + msg + "\n")

def main():
    ap = argparse.ArgumentParser(description="KernelX - Powering Smarter Disk Scheduling")
    ap.add_argument("-p", "--port", type=int, default=8000)
    ap.add_argument("--host", default="127.0.0.1", help="use 0.0.0.0 to share on LAN")
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args()
    try:
        srv = ThreadingHTTPServer((a.host, a.port), Handler)
    except OSError as e:
        sys.exit(f"Cannot bind {a.host}:{a.port} ({e}). Try another port: run -p 8080")
    url = f"http://{'localhost' if a.host in ('127.0.0.1','0.0.0.0') else a.host}:{a.port}/"
    print(f"\n  KernelX is live at {url}   (Ctrl+C to stop)\n")
    if not a.no_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()
