"""Scrape raw set piece counts from the Premier League API.

Fetches corners taken/conceded, free kicks won/conceded, and penalties
won/conceded per team per season from the official Premier League stats
API (footballapi.pulselive.com).

Usage:
    python scrape_pl_setpiece_counts.py

Output: data/pl_setpiece_counts.json
"""

import json
import os
import sys
import time
import urllib.request

API_BASE = "https://footballapi.pulselive.com/football/stats/ranked/teams"
HEADERS = {
    "Origin": "https://www.premierleague.com",
    "Content-Type": "application/json",
}

# Season label -> PL API compSeason ID (from 2014/15 onward to match Understat)
SEASONS = {
    "2014": {"label": "2014/2015", "id": 27},
    "2015": {"label": "2015/2016", "id": 42},
    "2016": {"label": "2016/2017", "id": 54},
    "2017": {"label": "2017/2018", "id": 79},
    "2018": {"label": "2018/2019", "id": 210},
    "2019": {"label": "2019/2020", "id": 274},
    "2020": {"label": "2020/2021", "id": 363},
    "2021": {"label": "2021/2022", "id": 418},
    "2022": {"label": "2022/2023", "id": 489},
    "2023": {"label": "2023/2024", "id": 578},
    "2024": {"label": "2024/2025", "id": 719},
}

STATS = {
    "corners_taken": "corner_taken",
    "freekicks_won": "fk_foul_won",
    "penalties_won": "penalty_won",
    "corners_conceded": "lost_corners",
    "freekicks_conceded": "fk_foul_lost",
    "penalties_conceded": "penalty_conceded",
}

# Map PL API team names to Understat names for joining
PL_TO_UNDERSTAT = {
    "Brighton & Hove Albion": "Brighton",
    "Tottenham Hotspur": "Tottenham",
    "West Bromwich Albion": "West Bromwich Albion",
    "Queens Park Rangers": "Queens Park Rangers",
    "Cardiff City": "Cardiff",
    "Huddersfield Town": "Huddersfield",
    "Norwich City": "Norwich",
    "West Ham United": "West Ham",
    "Leeds United": "Leeds",
    "Swansea City": "Swansea",
    "AFC Bournemouth": "Bournemouth",
    "Leicester City": "Leicester",
    "Hull City": "Hull",
    "Stoke City": "Stoke",
    "Luton Town": "Luton",
    "Ipswich Town": "Ipswich",
}


def normalize_team_name(pl_name):
    """Convert PL API team name to Understat-compatible name."""
    return PL_TO_UNDERSTAT.get(pl_name, pl_name)


def fetch_stat(stat_api_name, comp_season_id):
    """Fetch a single stat for a single season from the PL API."""
    url = (
        f"{API_BASE}/{stat_api_name}"
        f"?page=0&pageSize=40&compSeasons={comp_season_id}&comps=1&altIds=true"
    )
    req = urllib.request.Request(url, headers=HEADERS)
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read())
    entries = data.get("stats", {}).get("content", [])
    result = {}
    for entry in entries:
        team_name = entry["owner"]["name"]
        value = int(entry["value"])
        result[normalize_team_name(team_name)] = value
    return result


def main():
    results = {}

    for season_key, season_info in sorted(SEASONS.items()):
        label = season_info["label"]
        comp_id = season_info["id"]
        print(f"Fetching {label} (compSeason={comp_id})...", file=sys.stderr)

        season_data = {"season": label, "teams": {}}
        for our_name, api_name in STATS.items():
            try:
                stat_data = fetch_stat(api_name, comp_id)
                for team, value in stat_data.items():
                    if team not in season_data["teams"]:
                        season_data["teams"][team] = {"team": team}
                    season_data["teams"][team][our_name] = value
                print(f"  {our_name}: {len(stat_data)} teams", file=sys.stderr)
            except Exception as e:
                print(f"  Error fetching {our_name}: {e}", file=sys.stderr)
            time.sleep(0.3)

        # Convert teams dict to sorted list
        team_list = sorted(season_data["teams"].values(), key=lambda t: t.get("corners_taken", 0), reverse=True)
        # Ensure all stats present (default 0 for missing)
        for t in team_list:
            for stat_name in STATS:
                t.setdefault(stat_name, 0)
        season_data["teams"] = team_list
        results[season_key] = season_data
        print(f"  Got {len(team_list)} teams", file=sys.stderr)
        time.sleep(0.5)

    os.makedirs("data", exist_ok=True)
    with open("data/pl_setpiece_counts.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"Wrote {len(results)} seasons to data/pl_setpiece_counts.json", file=sys.stderr)


if __name__ == "__main__":
    main()
