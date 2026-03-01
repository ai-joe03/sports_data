#!/usr/bin/env python3
"""
Sports Analytics Server

Usage:
    python serve.py          # starts on port 8080
    python serve.py 9000     # custom port

Then open: http://localhost:8080/basketball/

API endpoints:
    GET /api/game/{game_id}  -> serves cached game data or fetches from FIBA LiveStats
    GET /api/season          -> aggregates all cached season games
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.request
import urllib.error
import json
import re
import sys
import os

PORT = 8080

DATA_ROOT       = r"C:\Users\ai_jo\Documents\sports-data"
BASKETBALL_DIR  = os.path.join(DATA_ROOT, "basketball")
SEASON_FILE     = os.path.join(BASKETBALL_DIR, "season_2526.json")
GAMES_DIR       = os.path.join(BASKETBALL_DIR, "games")
EPL_FILE        = os.path.join(DATA_ROOT, "all_seasons.json")


class ShotZoneHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        if re.match(r'^/api/season$', self.path):
            self._serve_season()
        elif re.match(r'^/api/epl$', self.path):
            self._serve_epl()
        else:
            m = re.match(r'^/api/game/(\d+)$', self.path)
            if m:
                self._proxy_game(m.group(1))
            else:
                super().do_GET()

    def _proxy_game(self, gid):
        cache_path = os.path.join(GAMES_DIR, f"{gid}.json")
        if os.path.exists(cache_path):
            print(f"  -> Serving {gid} from cache")
            try:
                with open(cache_path, "rb") as f:
                    body = f.read()
                self._respond(200, "application/json", body)
                return
            except Exception as e:
                print(f"  -> Cache read failed ({e}), falling through to FIBA")

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

    def _serve_season(self):
        try:
            if not os.path.exists(SEASON_FILE):
                self._respond_error(404, "season_2526.json not found")
                return

            with open(SEASON_FILE, "r", encoding="utf-8") as f:
                season_meta = json.load(f)

            game_ids = season_meta.get("game_ids", [])
            teams = {}
            shots = []

            for gid in game_ids:
                path = os.path.join(GAMES_DIR, f"{gid}.json")
                if not os.path.exists(path):
                    print(f"  -> Warning: game {gid} in season file but not cached — skipping")
                    continue
                with open(path, "r", encoding="utf-8") as f:
                    game = json.load(f)

                # Build teams dict keyed by team name
                for tid, info in game.get("teams", {}).items():
                    name = info["name"]
                    if name not in teams:
                        teams[name] = {"name": name, "short": info["short"]}

                # Add shots with team name and game_id
                for sh in game.get("shots", []):
                    tid = sh.get("team")
                    team_name = game["teams"].get(tid, {}).get("name", tid)
                    shots.append({**sh, "team": team_name, "game_id": gid})

            out = {
                "season":     season_meta.get("season", "2025/26"),
                "game_count": len(game_ids),
                "game_dates": season_meta.get("game_dates", {}),
                "teams":      teams,
                "shots":      shots,
                "total":      len(shots),
            }
            body = json.dumps(out).encode()
            self._respond(200, "application/json", body)
        except Exception as e:
            self._respond_error(500, str(e))

    def _serve_epl(self):
        try:
            if not os.path.exists(EPL_FILE):
                self._respond_error(404, "all_seasons.json not found")
                return
            with open(EPL_FILE, "r", encoding="utf-8") as f:
                body = f.read().encode()
            self._respond(200, "application/json", body)
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
