"""Scrape xG data for all EPL seasons available on Understat (2014-2024).

Fetches per-team breakdowns by situation (set pieces), shot zone, and
attack speed from Understat.

Usage:
    python scrape_all_seasons.py

Output: data/all_seasons.json
"""
import gzip, json, os, sys, time
import urllib.request

TEAM_API = "https://understat.com/getTeamData/{}/{}"
LEAGUE_API = "https://understat.com/getLeagueData/EPL/{}"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest",
    "Accept-Encoding": "gzip",
}

SET_PIECE_SITUATIONS = ["FromCorner", "SetPiece", "DirectFreekick", "Penalty"]


def fetch_json(url):
    """Fetch JSON from Understat API, handling gzip compression."""
    req = urllib.request.Request(url, headers=HEADERS)
    resp = urllib.request.urlopen(req, timeout=15)
    raw = resp.read()
    try:
        data = gzip.decompress(raw).decode("utf-8")
    except Exception:
        data = raw.decode("utf-8")
    return json.loads(data)


def extract_category(stats_group, category_keys=None):
    """Extract xG data from a stats group (situation, shotZone, attackSpeed).

    If category_keys is None, extracts all keys found in the group.
    Returns a dict of {key: {xG, goals, shots, against_xG, against_goals, against_shots}}.
    """
    if not stats_group:
        return {}
    keys = category_keys if category_keys else list(stats_group.keys())
    result = {}
    for key in keys:
        data = stats_group.get(key, {})
        against = data.get("against", {})
        result[key] = {
            "xG": round(float(data.get("xG", 0)), 2),
            "goals": int(data.get("goals", 0)),
            "shots": int(data.get("shots", 0)),
            "against_xG": round(float(against.get("xG", 0)), 2),
            "against_goals": int(against.get("goals", 0)),
            "against_shots": int(against.get("shots", 0)),
        }
    return result


def main():
    results = {}
    for season in range(2014, 2025):
        label = f"{season}/{season+1}"
        print(f"Fetching {label}...", file=sys.stderr)

        # Get team list for this season
        try:
            league_data = fetch_json(LEAGUE_API.format(season))
            teams_raw = league_data.get("teams", {})
            team_names = sorted(set(
                t.get("title", "") for t in teams_raw.values()
            ))
            if not team_names:
                print(f"  Skipping {label}: no teams found", file=sys.stderr)
                continue
        except Exception as e:
            print(f"  Skipping {label}: {e}", file=sys.stderr)
            continue

        season_teams = []
        for team_name in team_names:
            try:
                url_name = team_name.replace(" ", "_")
                team_data = fetch_json(TEAM_API.format(url_name, season))
                stats = team_data.get("statistics", {})
                entry = {"team": team_name}

                # Set piece situations (flat keys for backward compat)
                situation = stats.get("situation", {})
                for sit in SET_PIECE_SITUATIONS:
                    entry[sit] = extract_category(situation, [sit]).get(sit, {
                        "xG": 0, "goals": 0, "shots": 0,
                        "against_xG": 0, "against_goals": 0, "against_shots": 0,
                    })
                entry["total_setpiece_xG"] = round(sum(entry[s]["xG"] for s in SET_PIECE_SITUATIONS), 2)
                entry["total_setpiece_goals"] = sum(entry[s]["goals"] for s in SET_PIECE_SITUATIONS)
                entry["total_setpiece_against_xG"] = round(sum(entry[s]["against_xG"] for s in SET_PIECE_SITUATIONS), 2)

                # Shot zones (all keys found dynamically)
                shot_zone = stats.get("shotZone", {})
                entry["shotZone"] = extract_category(shot_zone)

                # Attack speed (all keys found dynamically)
                attack_speed = stats.get("attackSpeed", {})
                entry["attackSpeed"] = extract_category(attack_speed)

                season_teams.append(entry)
                time.sleep(0.3)
            except Exception as e:
                print(f"  Error {team_name}: {e}", file=sys.stderr)

        season_teams.sort(key=lambda r: r["total_setpiece_xG"], reverse=True)
        results[str(season)] = {"season": label, "teams": season_teams}
        print(f"  Got {len(season_teams)} teams", file=sys.stderr)
        time.sleep(0.5)

    os.makedirs("data", exist_ok=True)
    with open("data/all_seasons.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"Wrote {len(results)} seasons to data/all_seasons.json", file=sys.stderr)


if __name__ == "__main__":
    main()
