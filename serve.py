#!/usr/bin/env python3
"""
Super League Basketball — Shot Zone Server

Usage:
    python serve.py          # starts on port 8080
    python serve.py 9000     # custom port

Then open: http://localhost:8080/basketball_shots.html

API endpoint:
    GET /api/game/{game_id}  -> fetches & processes FIBA LiveStats data
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.request
import urllib.error
import json
import re
import sys
import os

PORT = 8080


class ShotZoneHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        m = re.match(r'^/api/game/(\d+)$', self.path)
        if m:
            self._proxy_game(m.group(1))
        else:
            super().do_GET()

    def _proxy_game(self, gid):
        url = f"http://www.fibalivestats.com/data/{gid}/data.json"
        print(f"  -> Fetching {url}")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                raw = r.read()
            data = json.loads(raw)
            out = _process_game(gid, data)
            body = json.dumps(out).encode()
            self._respond(200, "application/json", body)
        except urllib.error.HTTPError as e:
            self._respond_error(e.code, f"FIBA LiveStats returned {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            self._respond_error(503, f"Could not reach fibalivestats.com: {e.reason}")
        except Exception as e:
            self._respond_error(500, str(e))

    def _respond(self, code, content_type, body: bytes):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _respond_error(self, code, msg):
        body = json.dumps({"error": msg}).encode()
        self._respond(code, "application/json", body)

    def log_message(self, fmt, *args):
        print(f"  [{self.address_string()}] {fmt % args}")


def _process_game(gid, data):
    """Extract teams and shot events from raw FIBA LiveStats JSON.

    Shot coordinates come from tm[tid]['shot'], which stores x/y as
    normalised values 0-100 across the FULL court:
      x: 0 = left baseline, 100 = right baseline  (28 m)
      y: 0 = left sideline,  100 = right sideline  (15 m)
    Shots at x < 50 attack the left basket; x > 50 attack the right basket.
    """

    # --- Team info ---
    teams = {}
    for tid in ("1", "2"):
        t = data.get("tm", {}).get(tid, {})
        teams[tid] = {
            "name":  t.get("name", f"Team {tid}"),
            "short": t.get("shortName", t.get("name", f"T{tid}"))
        }

    shots = []

    # --- Extract from tm[tid]['shot'] (contains actual x/y court coords) ---
    for tid in ("1", "2"):
        for sh in data.get("tm", {}).get(tid, {}).get("shot", []):
            x = sh.get("x")
            y = sh.get("y")
            if x is None or y is None:
                continue
            shots.append({
                "team":   tid,
                "player": str(sh.get("player", "")).strip(),
                "made":   sh.get("r", 0) == 1,
                "type":   sh.get("actionType", ""),
                "sub":    sh.get("subType", ""),
                "x":      float(x),
                "y":      float(y),
                "period": sh.get("per", 0),
            })

    return {
        "game_id": gid,
        "teams":   teams,
        "shots":   shots,
        "total":   len(shots),
    }



if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    # Serve files from the script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or ".")
    srv = HTTPServer(("", port), ShotZoneHandler)
    print(f"\n  Sports Analytics Server")
    print(f"  Homepage:   http://localhost:{port}/")
    print(f"  EPL:        http://localhost:{port}/epl/")
    print(f"  Basketball: http://localhost:{port}/basketball/")
    print(f"  Stop:       Ctrl+C\n")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
