#!/usr/bin/env python3
"""
NEURA Demo Proxy — serves the demo page and proxies n8n API calls.
Usage: python3 proxy.py
Then open: http://localhost:8080
"""
import http.server, urllib.request, urllib.parse, os, json

N8N_BASE  = "http://localhost:5678"
API_KEY   = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4ZGUxMDMwNS0xOTI3LTRlM2MtYTNjNS1jMzI4NDMzNmMyOWMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiMDg0YjY1NzYtODVjYi00ZmUwLWJhYjEtODFjZGQ5MjAwNWU2IiwiaWF0IjoxNzgwNDE0OTAxLCJleHAiOjE3ODI5NjQ4MDB9.sMwfvZsjFqFah-z7BeOXozp9fEMS7sbK89EHALtSS_Q"
PORT      = 8080

# Holds the latest HITL payload pushed by n8n
hitl_data = None

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)

    def do_GET(self):
        if self.path.startswith("/n8n/"):
            self._proxy("GET")
        elif self.path == "/hitl":
            self._serve_hitl()
        else:
            super().do_GET()

    def do_POST(self):
        global hitl_data
        if self.path.startswith("/n8n/"):
            self._proxy("POST")
        elif self.path == "/hitl":
            # n8n pushes HITL data here
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                hitl_data = json.loads(body)
            except Exception:
                pass
            self.send_response(200); self._cors(); self.end_headers()
            self.wfile.write(b'{"ok":true}')
        elif self.path == "/hitl/clear":
            hitl_data = None
            self.send_response(200); self._cors(); self.end_headers()
            self.wfile.write(b'{"ok":true}')
        else:
            self.send_response(404); self.end_headers()

    def _serve_hitl(self):
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(hitl_data or {}).encode())

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def _proxy(self, method):
        n8n_path = self.path[4:]  # strip /n8n
        url = N8N_BASE + n8n_path
        body = None
        if method == "POST":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length else None
        req = urllib.request.Request(url, data=body, method=method)
        req.add_header("X-N8N-API-KEY", API_KEY)
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req) as resp:
                data = resp.read()
                self.send_response(resp.status)
                self._cors()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            data = e.read()
            self.send_response(e.code)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(data)

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-N8N-API-KEY")
        self.send_header("ngrok-skip-browser-warning", "true")

    def log_message(self, fmt, *args):
        pass  # suppress request logs

if __name__ == "__main__":
    with http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Handler) as srv:
        print(f"NEURA Demo running at http://localhost:{PORT}")
        print(f"Proxying n8n API calls to {N8N_BASE}")
        srv.serve_forever()
