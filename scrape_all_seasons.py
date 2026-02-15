"""Scrape set piece xG for all EPL seasons available on Understat (2014-2024)."""
import asyncio, json, sys
import aiohttp
from understat import Understat

SET_PIECE_SITUATIONS = ["FromCorner", "SetPiece", "DirectFreekick", "Penalty"]

async def main():
    results = {}
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)
        for season in range(2014, 2025):
            label = f"{season}/{season+1}"
            print(f"Fetching {label}...", file=sys.stderr)
            try:
                # Get team list for this season
                league_teams = await understat.get_teams("EPL", season)
                team_names = [t["title"] for t in league_teams]
            except Exception as e:
                print(f"  Skipping {label}: {e}", file=sys.stderr)
                continue

            season_teams = []
            for team_name in sorted(team_names):
                try:
                    stats = await understat.get_team_stats(team_name, season)
                    situation = stats.get("situation", {})
                    entry = {"team": team_name}
                    for sit in SET_PIECE_SITUATIONS:
                        data = situation.get(sit, {})
                        against = data.get("against", {})
                        entry[sit] = {
                            "xG": round(float(data.get("xG", 0)), 2),
                            "goals": int(data.get("goals", 0)),
                            "shots": int(data.get("shots", 0)),
                            "against_xG": round(float(against.get("xG", 0)), 2),
                            "against_goals": int(against.get("goals", 0)),
                            "against_shots": int(against.get("shots", 0)),
                        }
                    entry["total_setpiece_xG"] = round(sum(entry[s]["xG"] for s in SET_PIECE_SITUATIONS), 2)
                    entry["total_setpiece_goals"] = sum(entry[s]["goals"] for s in SET_PIECE_SITUATIONS)
                    entry["total_setpiece_against_xG"] = round(sum(entry[s]["against_xG"] for s in SET_PIECE_SITUATIONS), 2)
                    season_teams.append(entry)
                    await asyncio.sleep(0.3)
                except Exception as e:
                    print(f"  Error {team_name}: {e}", file=sys.stderr)

            season_teams.sort(key=lambda r: r["total_setpiece_xG"], reverse=True)
            results[str(season)] = {"season": label, "teams": season_teams}
            print(f"  Got {len(season_teams)} teams", file=sys.stderr)
            await asyncio.sleep(0.5)

    print(json.dumps(results))

asyncio.run(main())
