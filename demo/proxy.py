#!/usr/bin/env python3
"""
NEURA Demo Proxy — serves the demo page, proxies n8n API calls,
and runs a built-in demo simulation when n8n is not running.

Usage:   python3 proxy.py
Open:    http://localhost:8080/v3.html

Demo mode (no n8n needed):
  Just run the proxy and click Start Demo — it auto-detects whether
  n8n is available. If not, it simulates the full AI processing flow
  with pre-baked Sprint 7 meeting data.
"""
import http.server, urllib.request, urllib.parse, os, json, threading, time, socket

N8N_BASE  = "http://localhost:5678"
API_KEY   = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4ZGUxMDMwNS0xOTI3LTRlM2MtYTNjNS1jMzI4NDMzNmMyOWMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiMDg0YjY1NzYtODVjYi00ZmUwLWJhYjEtODFjZGQ5MjAwNWU2IiwiaWF0IjoxNzgwNDE0OTAxLCJleHAiOjE3ODI5NjQ4MDB9.sMwfvZsjFqFah-z7BeOXozp9fEMS7sbK89EHALtSS_Q"
PORT      = 8080

hitl_data = None  # latest HITL payload from n8n (or demo simulation)


# ─── Demo availability check ─────────────────────────────────────────────────

def is_n8n_running():
    try:
        port = int(N8N_BASE.rstrip("/").split(":")[-1])
        with socket.create_connection(("127.0.0.1", port), timeout=1):
            return True
    except Exception:
        return False


# ─── Pre-baked Sprint 7 demo data ────────────────────────────────────────────

DEMO_HITL = {
    "approve_url": "http://localhost:8080/demo/approve",
    "reject_url":  "http://localhost:8080/demo/reject",
    "meeting_summary": (
        "Sprint 7 integration review exposed three recurring blockers and two new external "
        "dependencies requiring formal action. The Bosch API documentation delay has now "
        "missed three consecutive sprints causing project-level impact — escalation is required. "
        "Six distinct action items were assigned with tight June 6–11 deadlines forming a "
        "critical dependency chain for the mandatory June 13 integration review."
    ),
    "internal_items": [
        {
            "task": "Complete full firmware integration and patch upon receipt of Bosch API docs and Jonas calibration constants",
            "owner_name": "Felix Wagner",
            "owner_email": "felix.wagner@neura-robotics.com",
            "is_external": False,
            "deadline": "2026-06-10",
            "priority": "critical",
            "depends_on": "Bosch API docs by June 6 + Jonas calibration constants by June 8",
            "channel": "teams_chat"
        },
        {
            "task": "Deliver corrected IMU calibration constants to Felix Wagner",
            "owner_name": "Jonas Mueller",
            "owner_email": "jonas.mueller@neura-robotics.com",
            "is_external": False,
            "deadline": "2026-06-08",
            "priority": "critical",
            "depends_on": None,
            "channel": "teams_chat"
        },
        {
            "task": "Conduct full power audit and deliver root cause analysis for 318W peak load (38W over 280W budget)",
            "owner_name": "Jonas Mueller",
            "owner_email": "jonas.mueller@neura-robotics.com",
            "is_external": False,
            "deadline": "2026-06-08",
            "priority": "high",
            "depends_on": None,
            "channel": "teams_chat"
        },
        {
            "task": "Prepare and send revision 3.1 mechanical specification sheet to Dr. Sarah Chen at Siemens PLM",
            "owner_name": "Jonas Mueller",
            "owner_email": "jonas.mueller@neura-robotics.com",
            "is_external": False,
            "deadline": "2026-06-07",
            "priority": "high",
            "depends_on": None,
            "channel": "teams_chat"
        },
        {
            "task": "Complete full QA integration test cycle and present results at Sprint QA review",
            "owner_name": "Anna Richter",
            "owner_email": "anna.richter@neura-robotics.com",
            "is_external": False,
            "deadline": "2026-06-11",
            "priority": "high",
            "depends_on": "Felix firmware patch by June 10 + Jonas calibration constants by June 8",
            "channel": "teams_chat"
        },
        {
            "task": "Obtain formal written API documentation commitment and June 13 attendance confirmation from Thomas Becker",
            "owner_name": "Maria Schmidt",
            "owner_email": "maria.schmidt@neura-robotics.com",
            "is_external": False,
            "deadline": "2026-06-03",
            "priority": "critical",
            "depends_on": None,
            "channel": "teams_chat"
        }
    ],
    "external_emails": [
        {
            "recipient_name": "Thomas Becker",
            "recipient_email": "thomas.becker@bosch.com",
            "company": "Bosch",
            "subject": "Formal Written Commitment Required — NEURA Robot Arm Integration API Documentation",
            "body": (
                "Dear Thomas,\n\n"
                "Following our Sprint 7 integration review today, I am writing to formally document "
                "the commitment you made in the meeting and to request written confirmation by close "
                "of business today.\n\n"
                "As discussed, this is the third consecutive sprint in which NEURA's integration work "
                "has been blocked waiting for the Bosch REST API documentation. As a direct result of "
                "the previous two delays, we missed the Sprint 6 integration milestone entirely, "
                "resulting in a two-week project delay and significant team downtime.\n\n"
                "Your commitments from today's meeting:\n"
                "• Complete REST API documentation and hardware interface specification — by Friday, 6 June 2026\n"
                "• Technical walkthrough call — week of 9 June 2026\n"
                "• Mandatory attendance at the Bosch Integration Review — Friday, 13 June 2026 at 09:00\n\n"
                "Please reply to this email today confirming these three points in writing.\n\n"
                "I must be direct: if the API documentation does not arrive by 6 June 2026, the "
                "13 June session will be escalated to an executive-level meeting between both "
                "organisations. We cannot allow this dependency to slip a fourth time.\n\n"
                "We value the partnership with Bosch and trust you will deliver on the commitments made today.\n\n"
                "Kind regards,\n"
                "Maria Schmidt\n"
                "Project Lead, Robot Arm Integration\n"
                "NEURA Robotics"
            ),
            "commitment_date": "2026-06-06",
            "urgency": "critical"
        },
        {
            "recipient_name": "Dr. Sarah Chen",
            "recipient_email": "sarah.chen@siemens.com",
            "company": "Siemens PLM",
            "subject": "Revision 3.1 Gripper Interface Specification — NEURA Robot Arm Digital Twin",
            "body": (
                "Dear Dr. Chen,\n\n"
                "Thank you for joining our Sprint 7 integration review today and for raising the "
                "specification discrepancy promptly.\n\n"
                "As agreed in the meeting, Jonas Mueller will prepare and send you the complete "
                "revision 3.1 mechanical specification for the NEURA gripper interface by "
                "Sunday, 7 June 2026. This is the current production target revision.\n\n"
                "Your confirmed deliverable upon receipt:\n"
                "• Validated digital twin simulation models for the end-effector assembly — by Thursday, 12 June 2026\n\n"
                "We would also appreciate written confirmation of your timeline, as discussed.\n\n"
                "Please do not hesitate to contact Jonas Mueller directly if you have any questions "
                "about the 3.1 specification once received.\n\n"
                "We look forward to a productive collaboration.\n\n"
                "Kind regards,\n"
                "Maria Schmidt\n"
                "Project Lead, Robot Arm Integration\n"
                "NEURA Robotics"
            ),
            "commitment_date": "2026-06-12",
            "urgency": "high"
        }
    ],
    "deadline_reminders": [
        {
            "title": "DEADLINE: Felix Wagner — Firmware Integration Patch",
            "owner_name": "Felix Wagner",
            "deadline": "2026-06-10",
            "priority": "critical",
            "reminder_note": "Critical path — QA test cycle and June 13 review both depend on this"
        },
        {
            "title": "DEADLINE: Jonas Mueller — IMU Calibration Constants",
            "owner_name": "Jonas Mueller",
            "deadline": "2026-06-08",
            "priority": "critical",
            "reminder_note": "Blocks Felix firmware patch (June 10) and Anna QA cycle"
        },
        {
            "title": "DEADLINE: Jonas Mueller — Power Audit Root Cause",
            "owner_name": "Jonas Mueller",
            "deadline": "2026-06-08",
            "priority": "high",
            "reminder_note": "Build 2.6 drawing 318W vs 280W target — recurring issue"
        },
        {
            "title": "DEADLINE: Jonas Mueller — Rev 3.1 Spec to Siemens PLM",
            "owner_name": "Jonas Mueller",
            "deadline": "2026-06-07",
            "priority": "high",
            "reminder_note": "Siemens PLM simulation models blocked without this spec"
        },
        {
            "title": "DEADLINE: Thomas Becker — Bosch API Documentation",
            "owner_name": "Thomas Becker",
            "deadline": "2026-06-06",
            "priority": "critical",
            "reminder_note": "Third consecutive sprint delay — executive escalation if missed"
        },
        {
            "title": "DEADLINE: Anna Richter — QA Test Cycle Complete",
            "owner_name": "Anna Richter",
            "deadline": "2026-06-11",
            "priority": "high",
            "reminder_note": "Results must be presented at Sprint QA review on June 11"
        }
    ],
    "calendar_check": {
        "title": "Bosch Integration Review — Sprint 7 Follow-up",
        "date": "2026-06-13",
        "time": "09:00",
        "duration_minutes": 60,
        "agenda": "Verify Bosch API documentation delivery, confirm firmware integration status, review QA results",
        "is_free": True,
        "availability_note": "✅ Calendar confirmed available on 2026-06-13 at 09:00",
        "conflict_count": 0,
        "conflict_subjects": [],
        "suggested_times": []
    },
    "follow_up_meeting": {
        "title": "Bosch Integration Review — Sprint 7 Follow-up",
        "date": "2026-06-13",
        "time": "09:00",
        "duration_minutes": 60,
        "attendees": [
            "felix.wagner@neura-robotics.com",
            "thomas.becker@bosch.com",
            "maria.schmidt@neura-robotics.com"
        ],
        "agenda": "Verify Bosch API documentation delivery, confirm firmware integration status, review QA results"
    },
    "external_participants": ["Thomas Becker (Bosch)", "Dr. Sarah Chen (Siemens PLM)"],
    "has_external": True,
    "item_count": 8,
    "blockers": [
        {
            "description": "Bosch REST API documentation — third consecutive sprint delay",
            "owner": "Thomas Becker (Bosch)",
            "occurrences": 3,
            "escalation_needed": True,
            "is_recurring": True
        },
        {
            "description": "IMU sensor calibration drift — returned after Sprint 5 supposed fix",
            "owner": "Jonas Mueller",
            "occurrences": 2,
            "escalation_needed": False,
            "is_recurring": True
        },
        {
            "description": "Power consumption regression (318W vs 280W target)",
            "owner": "Jonas Mueller",
            "occurrences": 2,
            "escalation_needed": False,
            "is_recurring": True
        }
    ],
    "escalation_required": True,
    "escalation_reason": (
        "Bosch API documentation has missed three consecutive sprint milestones causing "
        "project-level delays. Escalation to executive level is required if the June 6 deadline is missed."
    )
}

# Conflict scenario — swap calendar_check to this to demo the conflict UI
DEMO_HITL_CONFLICT = dict(DEMO_HITL)
DEMO_HITL_CONFLICT["calendar_check"] = {
    "title": "Bosch Integration Review — Sprint 7 Follow-up",
    "date": "2026-06-13",
    "time": "09:00",
    "duration_minutes": 60,
    "agenda": "Verify Bosch API documentation delivery, confirm firmware integration status, review QA results",
    "is_free": False,
    "availability_note": "⚠ CONFLICT on 2026-06-13 09:00: \"All-hands Town Hall\" — time slot unavailable",
    "conflict_count": 1,
    "conflict_subjects": ["All-hands Town Hall"],
    "suggested_times": [
        {"label": "Same day — afternoon",  "date": "2026-06-13", "time": "14:00", "datetime": "2026-06-13T14:00:00", "display": "June 13 at 14:00–15:00"},
        {"label": "Next day — morning",    "date": "2026-06-14", "time": "09:00", "datetime": "2026-06-14T09:00:00", "display": "June 14 at 09:00–10:00"},
        {"label": "Next day — afternoon",  "date": "2026-06-14", "time": "14:00", "datetime": "2026-06-14T14:00:00", "display": "June 14 at 14:00–15:00"},
        {"label": "+2 days — morning",     "date": "2026-06-15", "time": "09:00", "datetime": "2026-06-15T09:00:00", "display": "June 15 at 09:00–10:00"}
    ]
}


# ─── Demo simulation ──────────────────────────────────────────────────────────

def _run_demo_simulation(use_conflict=False):
    """Background thread: pushes pre-baked HITL data after a realistic delay."""
    global hitl_data
    time.sleep(17)  # matches the HTML animation timing (~13s of steps + buffer)
    hitl_data = DEMO_HITL_CONFLICT if use_conflict else DEMO_HITL
    print(f"[demo] HITL data pushed ({'conflict' if use_conflict else 'free'} scenario)")


# ─── HTTP handler ─────────────────────────────────────────────────────────────

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)

    # ── GET ──────────────────────────────────────────────────────────────────
    def do_GET(self):
        if self.path.startswith("/n8n/"):
            self._proxy("GET")
        elif self.path == "/hitl":
            self._serve_hitl()
        elif self.path.startswith("/demo/mode"):
            use_conflict = "conflict=1" in self.path
            threading.Thread(target=_run_demo_simulation, args=(use_conflict,), daemon=True).start()
            self._json_ok({"mode": "conflict" if use_conflict else "free", "eta": 17})
        elif "action=approve" in self.path or "action=reject" in self.path:
            # Email link clicked — call n8n SERVER-SIDE (no CORS, no silent failures)
            self._handle_email_action()
        else:
            super().do_GET()

    def _handle_email_action(self):
        """Handle approval/rejection coming from the email link.
        Calls n8n server-side (Python → n8n), then serves a clean confirmation page."""
        from urllib.parse import urlparse, parse_qs, unquote
        parsed = urlparse("http://localhost" + self.path)
        params  = parse_qs(parsed.query)
        action  = params.get("action", [None])[0]
        n8n_url = params.get("n8n",    [None])[0]

        ok = (action == "approve")
        n8n_called = False

        if n8n_url:
            decoded = unquote(n8n_url)
            print(f"[email] {action} — calling n8n: {decoded[:80]}...")
            try:
                req = urllib.request.Request(decoded, method="GET")
                req.add_header("User-Agent", "NEURA-Proxy/1.0")
                with urllib.request.urlopen(req, timeout=10) as resp:
                    n8n_called = True
                    print(f"[email] n8n responded: {resp.status}")
            except Exception as e:
                print(f"[email] n8n call failed: {e}")

        # Serve a self-contained confirmation page (no JS needed)
        color   = "#1a7f37" if ok else "#cf222e"
        icon    = "✅"       if ok else "❌"
        title   = "Approved!" if ok else "Rejected"
        msg     = ("Your approval has been sent. Emails are being delivered "
                   "and the Teams meeting is being created."
                   if ok else
                   "You rejected the distribution. Nothing was sent.")
        warn    = ("" if n8n_called else
                   "<p style='color:#9a6700;background:#fff8c5;padding:10px;border-radius:6px;"
                   "margin-top:20px;font-size:14px'>⚠ Could not reach n8n — make sure n8n is "
                   "running and try approving again from the demo page.</p>")
        html = (f"<!DOCTYPE html><html><head><meta charset='UTF-8'>"
                f"<title>NEURA Meeting Agent</title>"
                f"<style>body{{font-family:Arial,sans-serif;text-align:center;"
                f"padding:80px 20px;background:#fff}}"
                f".icon{{font-size:64px;margin-bottom:20px}}"
                f".title{{font-size:28px;font-weight:700;color:{color}}}"
                f".msg{{font-size:16px;color:#555;margin-top:12px;line-height:1.6}}"
                f".foot{{margin-top:60px;color:#aaa;font-size:12px}}</style></head>"
                f"<body><div class='icon'>{icon}</div>"
                f"<div class='title'>{title}</div>"
                f"<div class='msg'>{msg}{warn}</div>"
                f"<div class='foot'>NEURA Meeting Intelligence · Built by Futurice · "
                f"GPT-4o + Microsoft Graph API + n8n</div>"
                f"</body></html>")
        data = html.encode()
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # ── POST ─────────────────────────────────────────────────────────────────
    def do_POST(self):
        global hitl_data
        path = self.path.split("?")[0]

        if self.path.startswith("/n8n/"):
            self._proxy("POST")

        elif path == "/hitl":
            # n8n pushes HITL data here (real workflow mode)
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                hitl_data = json.loads(body)
                print("[hitl] Received data from n8n")
            except Exception:
                pass
            self.send_response(200); self._cors(); self.end_headers()
            self.wfile.write(b'{"ok":true}')

        elif path == "/hitl/clear":
            hitl_data = None
            self.send_response(200); self._cors(); self.end_headers()
            self.wfile.write(b'{"ok":true}')

        elif path == "/hitl/approve":
            # UI Approve button — call n8n server-side (avoids browser CORS issues)
            length = int(self.headers.get("Content-Length", 0))
            body_raw = self.rfile.read(length) if length else b""
            n8n_url = (hitl_data or {}).get("approve_url", "")
            if n8n_url and "localhost:8080" not in n8n_url:
                print(f"[hitl/approve] Calling n8n: {n8n_url[:80]}...")
                try:
                    req = urllib.request.Request(n8n_url, data=body_raw, method="POST")
                    req.add_header("Content-Type", "application/json")
                    with urllib.request.urlopen(req, timeout=15) as resp:
                        print(f"[hitl/approve] n8n resumed: {resp.status}")
                except Exception as e:
                    print(f"[hitl/approve] n8n call failed: {e}")
            else:
                print("[hitl/approve] Demo mode — approved (no n8n call needed)")
            hitl_data = None
            self._json_ok({"ok": True})

        elif path == "/hitl/reject":
            # UI Reject button — call n8n server-side
            length = int(self.headers.get("Content-Length", 0))
            if length: self.rfile.read(length)
            n8n_url = (hitl_data or {}).get("reject_url", "")
            if n8n_url and "localhost:8080" not in n8n_url:
                print(f"[hitl/reject] Calling n8n: {n8n_url[:80]}...")
                try:
                    req = urllib.request.Request(n8n_url, method="GET")
                    with urllib.request.urlopen(req, timeout=15) as resp:
                        print(f"[hitl/reject] n8n resumed: {resp.status}")
                except Exception as e:
                    print(f"[hitl/reject] n8n call failed: {e}")
            else:
                print("[hitl/reject] Demo mode — rejected (no n8n call needed)")
            hitl_data = None
            self._json_ok({"ok": True})

        elif path == "/demo/start":
            # Start demo: use real n8n if available, otherwise simulate
            if is_n8n_running():
                print("[demo] n8n is running — forwarding trigger to n8n")
                self._trigger_n8n()
            else:
                # Parse optional body for scenario config
                length = int(self.headers.get("Content-Length", 0))
                body_raw = self.rfile.read(length) if length else b""
                use_conflict = False
                try:
                    body_json = json.loads(body_raw)
                    use_conflict = bool(body_json.get("conflict"))
                except Exception:
                    pass
                hitl_data = None  # clear previous run
                threading.Thread(
                    target=_run_demo_simulation,
                    args=(use_conflict,),
                    daemon=True
                ).start()
                print(f"[demo] Simulation started ({'conflict' if use_conflict else 'free'} scenario, ~17s)")
                self._json_ok({"mode": "demo", "n8n": False, "eta": 17})

        elif path == "/demo/approve":
            # Human approved — in demo mode just log and return success
            length = int(self.headers.get("Content-Length", 0))
            if length:
                body_raw = self.rfile.read(length)
                try:
                    edited = json.loads(body_raw)
                    has_edits = any([
                        edited.get("edited_items") != (DEMO_HITL.get("internal_items")),
                        edited.get("edited_emails") != (DEMO_HITL.get("external_emails")),
                        edited.get("edited_meeting") is not None
                    ])
                    print(f"[demo] Approved {'with edits' if has_edits else '(no changes)'}")
                except Exception:
                    print("[demo] Approved")
            hitl_data = None
            self._json_ok({"ok": True, "status": "approved"})

        elif path == "/demo/reject":
            hitl_data = None
            print("[demo] Rejected by human")
            self._json_ok({"ok": True, "status": "rejected"})

        else:
            self.send_response(404); self.end_headers()

    # ── OPTIONS (CORS preflight) ──────────────────────────────────────────────
    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _serve_hitl(self):
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(hitl_data or {}).encode())

    def _json_ok(self, payload):
        data = json.dumps(payload).encode()
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(data)

    def _trigger_n8n(self):
        """Forward the demo start trigger to the n8n webhook."""
        url = N8N_BASE + "/webhook/neura-demo-trigger-v3"
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=5) as _:
                pass
            self._json_ok({"mode": "n8n", "n8n": True})
        except Exception as e:
            print(f"[demo] n8n trigger failed: {e} — falling back to simulation")
            threading.Thread(target=_run_demo_simulation, args=(False,), daemon=True).start()
            self._json_ok({"mode": "demo_fallback", "n8n": False, "eta": 17})

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
        pass  # suppress per-request logs


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    n8n_status = "n8n detected ✓" if is_n8n_running() else "n8n not running — demo simulation mode"
    print(f"NEURA Demo Proxy running at http://localhost:{PORT}")
    print(f"Open: http://localhost:{PORT}/v3.html")
    print(f"Mode: {n8n_status}")
    print(f"Conflict demo: http://localhost:{PORT}/demo/mode?conflict=1")
    with http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Handler) as srv:
        srv.serve_forever()
