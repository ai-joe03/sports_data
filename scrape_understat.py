"""
Scrape set piece xG data from Understat for all EPL teams.
Outputs JSON that feeds the D3 visualization.

Usage:
    pip install aiohttp understat
    python scrape_understat.py [--season 2024]

Output: data/epl_setpiece_xg.json
"""

import asyncio
import json
import os
import sys

import aiohttp
from understat import Understat

EPL_TEAMS_BY_SEASON = {
    2024: [
        "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton",
        "Chelsea", "Crystal Palace", "Everton", "Fulham", "Ipswich Town",
        "Leicester", "Liverpool", "Manchester City", "Manchester United",
        "Newcastle United", "Nottingham Forest", "Southampton", "Tottenham",
        "West Ham", "Wolverhampton Wanderers",
    ],
    2023: [
        "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton",
        "Burnley", "Chelsea", "Crystal Palace", "Everton", "Fulham",
        "Liverpool", "Luton", "Manchester City", "Manchester United",
        "Newcastle United", "Nottingham Forest", "Sheffield United",
        "Tottenham", "West Ham", "Wolverhampton Wanderers",
    ],
}

SET_PIECE_SITUATIONS = ["FromCorner", "SetPiece", "DirectFreekick", "Penalty"]


async def fetch_team_stats(session, understat, team, season):
    """Fetch situation-level stats for a single team."""
    try:
        stats = await understat.get_team_stats(team, season)
        situation = stats.get("situation", {})
        result = {"team": team}
        for sit in SET_PIECE_SITUATIONS:
            data = situation.get(sit, {})
            result[sit] = {
                "xG": round(float(data.get("xG", 0)), 2),
                "goals": int(data.get("goals", 0)),
                "shots": int(data.get("shots", 0)),
                "against_xG": round(float(data.get("against", {}).get("xG", 0)), 2),
                "against_goals": int(data.get("against", {}).get("goals", 0)),
                "against_shots": int(data.get("against", {}).get("shots", 0)),
            }
        # Compute totals
        result["total_setpiece_xG"] = round(
            sum(result[s]["xG"] for s in SET_PIECE_SITUATIONS), 2
        )
        result["total_setpiece_goals"] = sum(
            result[s]["goals"] for s in SET_PIECE_SITUATIONS
        )
        result["total_setpiece_against_xG"] = round(
            sum(result[s]["against_xG"] for s in SET_PIECE_SITUATIONS), 2
        )
        return result
    except Exception as e:
        print(f"  [ERROR] {team}: {e}", file=sys.stderr)
        return None


async def main(season=2024):
    teams = EPL_TEAMS_BY_SEASON.get(season)
    if not teams:
        print(f"No team list for season {season}. Add it to EPL_TEAMS_BY_SEASON.")
        sys.exit(1)

    print(f"Fetching set piece xG for {len(teams)} EPL teams ({season}/{season+1})...")
    results = []

    async with aiohttp.ClientSession() as session:
        understat = Understat(session)
        for team in teams:
            print(f"  Fetching {team}...")
            result = await fetch_team_stats(session, understat, team, season)
            if result:
                results.append(result)
            await asyncio.sleep(1)  # be polite

    results.sort(key=lambda r: r["total_setpiece_xG"], reverse=True)

    os.makedirs("data", exist_ok=True)
    outpath = f"data/epl_setpiece_xg_{season}.json"
    with open(outpath, "w") as f:
        json.dump({"season": f"{season}/{season+1}", "teams": results}, f, indent=2)

    print(f"\nDone! Wrote {len(results)} teams to {outpath}")


if __name__ == "__main__":
    season = int(sys.argv[1].replace("--season=", "").replace("--season", "").strip()) if len(sys.argv) > 1 else 2024
    asyncio.run(main(season))
