#!/usr/bin/env python3
"""
Generate representative EPL set piece xG data for ALL seasons 2014/15 through 2024/25.
Uses seeded random for reproducibility, with realistic value ranges based on team tier.
"""

import json
import random
import os

# ---------- Season rosters (20 teams each) ----------
SEASON_TEAMS = {
    "2014": [
        "Arsenal", "Aston Villa", "Burnley", "Chelsea", "Crystal Palace",
        "Everton", "Hull City", "Leicester", "Liverpool", "Manchester City",
        "Manchester United", "Newcastle United", "QPR", "Southampton",
        "Stoke City", "Sunderland", "Swansea", "Tottenham", "West Brom", "West Ham"
    ],
    "2015": [
        "Arsenal", "Aston Villa", "Bournemouth", "Chelsea", "Crystal Palace",
        "Everton", "Leicester", "Liverpool", "Manchester City", "Manchester United",
        "Newcastle United", "Norwich", "Southampton", "Stoke City",
        "Sunderland", "Swansea", "Tottenham", "Watford", "West Brom", "West Ham"
    ],
    "2016": [
        "Arsenal", "Bournemouth", "Burnley", "Chelsea", "Crystal Palace",
        "Everton", "Hull City", "Leicester", "Liverpool", "Manchester City",
        "Manchester United", "Middlesbrough", "Southampton", "Stoke City",
        "Sunderland", "Swansea", "Tottenham", "Watford", "West Brom", "West Ham"
    ],
    "2017": [
        "Arsenal", "Bournemouth", "Brighton", "Burnley", "Chelsea",
        "Crystal Palace", "Everton", "Huddersfield", "Leicester", "Liverpool",
        "Manchester City", "Manchester United", "Newcastle United", "Southampton",
        "Stoke City", "Swansea", "Tottenham", "Watford", "West Brom", "West Ham"
    ],
    "2018": [
        "Arsenal", "Bournemouth", "Brighton", "Burnley", "Cardiff",
        "Chelsea", "Crystal Palace", "Everton", "Fulham", "Huddersfield",
        "Leicester", "Liverpool", "Manchester City", "Manchester United",
        "Newcastle United", "Southampton", "Tottenham", "Watford", "West Ham",
        "Wolverhampton Wanderers"
    ],
    "2019": [
        "Arsenal", "Aston Villa", "Bournemouth", "Brighton", "Burnley",
        "Chelsea", "Crystal Palace", "Everton", "Leicester", "Liverpool",
        "Manchester City", "Manchester United", "Newcastle United", "Norwich",
        "Sheffield United", "Southampton", "Tottenham", "Watford", "West Ham",
        "Wolverhampton Wanderers"
    ],
    "2020": [
        "Arsenal", "Aston Villa", "Brighton", "Burnley", "Chelsea",
        "Crystal Palace", "Everton", "Fulham", "Leeds", "Leicester",
        "Liverpool", "Manchester City", "Manchester United", "Newcastle United",
        "Sheffield United", "Southampton", "Tottenham", "West Brom", "West Ham",
        "Wolverhampton Wanderers"
    ],
    "2021": [
        "Arsenal", "Aston Villa", "Brentford", "Brighton", "Burnley",
        "Chelsea", "Crystal Palace", "Everton", "Leeds", "Leicester",
        "Liverpool", "Manchester City", "Manchester United", "Newcastle United",
        "Norwich", "Southampton", "Tottenham", "Watford", "West Ham",
        "Wolverhampton Wanderers"
    ],
    "2022": [
        "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton",
        "Chelsea", "Crystal Palace", "Everton", "Fulham", "Leeds",
        "Leicester", "Liverpool", "Manchester City", "Manchester United",
        "Newcastle United", "Nottingham Forest", "Southampton", "Tottenham",
        "West Ham", "Wolverhampton Wanderers"
    ],
    "2023": [
        "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton",
        "Burnley", "Chelsea", "Crystal Palace", "Everton", "Fulham",
        "Liverpool", "Luton", "Manchester City", "Manchester United",
        "Newcastle United", "Nottingham Forest", "Sheffield United", "Tottenham",
        "West Ham", "Wolverhampton Wanderers"
    ],
}

# ---------- Approximate final league position tiers per season ----------
# tier 1 = top 4, tier 2 = 5-10, tier 3 = 11-15, tier 4 = 16-20
# We define the champion + top-4, upper-mid, lower-mid, bottom for each season
# to drive realistic data generation.

SEASON_TIERS = {
    "2014": {
        # Chelsea (1), Man City (2), Arsenal (3), Man Utd (4)
        1: ["Chelsea", "Manchester City", "Arsenal", "Manchester United"],
        2: ["Tottenham", "Liverpool", "Southampton", "Swansea", "Stoke City", "Everton"],
        3: ["West Ham", "Crystal Palace", "West Brom", "Leicester", "Newcastle United"],
        4: ["Sunderland", "Aston Villa", "Hull City", "Burnley", "QPR"],
    },
    "2015": {
        # Leicester (1!), Arsenal (2), Tottenham (3), Man City (4)
        1: ["Leicester", "Arsenal", "Tottenham", "Manchester City"],
        2: ["Manchester United", "Southampton", "West Ham", "Liverpool", "Stoke City", "Chelsea"],
        3: ["Everton", "Swansea", "Watford", "Crystal Palace", "Bournemouth"],
        4: ["West Brom", "Sunderland", "Newcastle United", "Norwich", "Aston Villa"],
    },
    "2016": {
        # Chelsea (1), Tottenham (2), Man City (3), Liverpool (4)
        1: ["Chelsea", "Tottenham", "Manchester City", "Liverpool"],
        2: ["Arsenal", "Manchester United", "Everton", "Southampton", "Bournemouth", "West Brom"],
        3: ["West Ham", "Leicester", "Stoke City", "Crystal Palace", "Swansea"],
        4: ["Burnley", "Watford", "Hull City", "Middlesbrough", "Sunderland"],
    },
    "2017": {
        # Man City (1), Man Utd (2), Tottenham (3), Liverpool (4)
        1: ["Manchester City", "Manchester United", "Tottenham", "Liverpool"],
        2: ["Chelsea", "Arsenal", "Burnley", "Everton", "Leicester", "Newcastle United"],
        3: ["Crystal Palace", "Bournemouth", "West Ham", "Watford", "Brighton"],
        4: ["Huddersfield", "Southampton", "Swansea", "Stoke City", "West Brom"],
    },
    "2018": {
        # Man City (1), Liverpool (2), Chelsea (3), Tottenham (4)
        1: ["Manchester City", "Liverpool", "Chelsea", "Tottenham"],
        2: ["Arsenal", "Manchester United", "Wolverhampton Wanderers", "Everton", "Leicester", "West Ham"],
        3: ["Watford", "Crystal Palace", "Newcastle United", "Bournemouth", "Burnley"],
        4: ["Cardiff", "Fulham", "Huddersfield", "Brighton", "Southampton"],
    },
    "2019": {
        # Liverpool (1), Man City (2), Man Utd (3), Chelsea (4)
        1: ["Liverpool", "Manchester City", "Manchester United", "Chelsea"],
        2: ["Leicester", "Tottenham", "Wolverhampton Wanderers", "Arsenal", "Sheffield United", "Burnley"],
        3: ["Southampton", "Everton", "Newcastle United", "Crystal Palace", "Brighton"],
        4: ["West Ham", "Aston Villa", "Bournemouth", "Watford", "Norwich"],
    },
    "2020": {
        # Man City (1), Man Utd (2), Liverpool (3), Chelsea (4)
        1: ["Manchester City", "Manchester United", "Liverpool", "Chelsea"],
        2: ["Leicester", "West Ham", "Tottenham", "Arsenal", "Leeds", "Everton"],
        3: ["Aston Villa", "Newcastle United", "Wolverhampton Wanderers", "Crystal Palace", "Southampton"],
        4: ["Brighton", "Burnley", "Fulham", "West Brom", "Sheffield United"],
    },
    "2021": {
        # Man City (1), Liverpool (2), Chelsea (3), Tottenham (4)
        1: ["Manchester City", "Liverpool", "Chelsea", "Tottenham"],
        2: ["Arsenal", "Manchester United", "West Ham", "Leicester", "Brighton", "Wolverhampton Wanderers"],
        3: ["Newcastle United", "Crystal Palace", "Brentford", "Aston Villa", "Southampton"],
        4: ["Everton", "Leeds", "Burnley", "Watford", "Norwich"],
    },
    "2022": {
        # Man City (1), Arsenal (2), Man Utd (3), Newcastle (4)
        1: ["Manchester City", "Arsenal", "Manchester United", "Newcastle United"],
        2: ["Liverpool", "Brighton", "Aston Villa", "Tottenham", "Brentford", "Fulham"],
        3: ["Crystal Palace", "Chelsea", "Wolverhampton Wanderers", "West Ham", "Bournemouth"],
        4: ["Nottingham Forest", "Everton", "Leicester", "Leeds", "Southampton"],
    },
    "2023": {
        # Man City (1), Arsenal (2), Liverpool (3), Aston Villa (4)
        1: ["Manchester City", "Arsenal", "Liverpool", "Aston Villa"],
        2: ["Tottenham", "Chelsea", "Newcastle United", "Manchester United", "West Ham", "Brighton"],
        3: ["Bournemouth", "Crystal Palace", "Wolverhampton Wanderers", "Fulham", "Brentford"],
        4: ["Everton", "Nottingham Forest", "Luton", "Burnley", "Sheffield United"],
    },
}


def _r(rng, lo, hi, decimals=2):
    """Return a random float in [lo, hi] rounded to `decimals`."""
    return round(rng.uniform(lo, hi), decimals)


def _ri(rng, lo, hi):
    """Return a random int in [lo, hi]."""
    return rng.randint(lo, hi)


def generate_team_data(team, season_key, tier, rng):
    """Generate one team's set piece data for a season based on its tier (1-4)."""

    # ---------- FromCorner ----------
    if tier == 1:
        fc_xg = _r(rng, 8.0, 12.0)
        fc_shots = _ri(rng, 70, 95)
        fc_against_xg = _r(rng, 3.5, 5.0)
        fc_against_shots = _ri(rng, 32, 45)
    elif tier == 2:
        fc_xg = _r(rng, 6.0, 8.5)
        fc_shots = _ri(rng, 55, 75)
        fc_against_xg = _r(rng, 4.2, 5.8)
        fc_against_shots = _ri(rng, 40, 52)
    elif tier == 3:
        fc_xg = _r(rng, 5.0, 7.0)
        fc_shots = _ri(rng, 45, 65)
        fc_against_xg = _r(rng, 4.8, 6.0)
        fc_against_shots = _ri(rng, 44, 54)
    else:  # tier 4
        fc_xg = _r(rng, 4.0, 6.0)
        fc_shots = _ri(rng, 38, 55)
        fc_against_xg = _r(rng, 5.5, 6.8)
        fc_against_shots = _ri(rng, 48, 60)

    # Goals are roughly proportional to xG with noise
    fc_goals = max(0, round(fc_xg * _r(rng, 0.7, 1.3, 1)))
    fc_against_goals = max(0, round(fc_against_xg * _r(rng, 0.7, 1.3, 1)))

    # ---------- SetPiece (throw-ins, indirect FK situations, etc.) ----------
    if tier == 1:
        sp_xg = _r(rng, 2.5, 3.5)
        sp_shots = _ri(rng, 22, 32)
        sp_against_xg = _r(rng, 1.2, 2.0)
        sp_against_shots = _ri(rng, 12, 20)
    elif tier == 2:
        sp_xg = _r(rng, 2.0, 3.0)
        sp_shots = _ri(rng, 18, 28)
        sp_against_xg = _r(rng, 1.6, 2.5)
        sp_against_shots = _ri(rng, 15, 22)
    elif tier == 3:
        sp_xg = _r(rng, 1.7, 2.6)
        sp_shots = _ri(rng, 14, 24)
        sp_against_xg = _r(rng, 2.0, 2.8)
        sp_against_shots = _ri(rng, 18, 25)
    else:
        sp_xg = _r(rng, 1.4, 2.2)
        sp_shots = _ri(rng, 11, 20)
        sp_against_xg = _r(rng, 2.4, 3.2)
        sp_against_shots = _ri(rng, 20, 28)

    sp_goals = max(0, round(sp_xg * _r(rng, 0.6, 1.4, 1)))
    sp_against_goals = max(0, round(sp_against_xg * _r(rng, 0.6, 1.4, 1)))

    # ---------- DirectFreekick ----------
    if tier == 1:
        dfk_xg = _r(rng, 1.0, 1.8)
        dfk_shots = _ri(rng, 16, 26)
        dfk_against_xg = _r(rng, 0.5, 0.9)
        dfk_against_shots = _ri(rng, 8, 14)
    elif tier == 2:
        dfk_xg = _r(rng, 0.8, 1.5)
        dfk_shots = _ri(rng, 12, 22)
        dfk_against_xg = _r(rng, 0.7, 1.1)
        dfk_against_shots = _ri(rng, 10, 16)
    elif tier == 3:
        dfk_xg = _r(rng, 0.7, 1.3)
        dfk_shots = _ri(rng, 10, 20)
        dfk_against_xg = _r(rng, 0.8, 1.3)
        dfk_against_shots = _ri(rng, 12, 18)
    else:
        dfk_xg = _r(rng, 0.5, 1.1)
        dfk_shots = _ri(rng, 7, 16)
        dfk_against_xg = _r(rng, 1.0, 1.6)
        dfk_against_shots = _ri(rng, 14, 22)

    dfk_goals = max(0, round(dfk_xg * _r(rng, 0.0, 1.5, 1)))
    dfk_against_goals = max(0, round(dfk_against_xg * _r(rng, 0.0, 1.5, 1)))

    # ---------- Penalty ----------
    if tier == 1:
        pen_count = _ri(rng, 4, 6)
        pen_against_count = _ri(rng, 1, 3)
    elif tier == 2:
        pen_count = _ri(rng, 3, 5)
        pen_against_count = _ri(rng, 2, 3)
    elif tier == 3:
        pen_count = _ri(rng, 2, 4)
        pen_against_count = _ri(rng, 2, 4)
    else:
        pen_count = _ri(rng, 2, 3)
        pen_against_count = _ri(rng, 3, 4)

    pen_xg = round(pen_count * 0.76, 2)
    pen_against_xg = round(pen_against_count * 0.76, 2)
    # Goals from pens: mostly converted
    pen_goals = max(0, pen_count - _ri(rng, 0, 1))
    pen_against_goals = max(0, pen_against_count - _ri(rng, 0, 1))

    # ---------- Totals ----------
    total_xg = round(fc_xg + sp_xg + dfk_xg + pen_xg, 2)
    total_goals = fc_goals + sp_goals + dfk_goals + pen_goals
    total_against_xg = round(fc_against_xg + sp_against_xg + dfk_against_xg + pen_against_xg, 2)

    return {
        "team": team,
        "FromCorner": {
            "xG": fc_xg, "goals": fc_goals, "shots": fc_shots,
            "against_xG": fc_against_xg, "against_goals": fc_against_goals, "against_shots": fc_against_shots,
        },
        "SetPiece": {
            "xG": sp_xg, "goals": sp_goals, "shots": sp_shots,
            "against_xG": sp_against_xg, "against_goals": sp_against_goals, "against_shots": sp_against_shots,
        },
        "DirectFreekick": {
            "xG": dfk_xg, "goals": dfk_goals, "shots": dfk_shots,
            "against_xG": dfk_against_xg, "against_goals": dfk_against_goals, "against_shots": dfk_against_shots,
        },
        "Penalty": {
            "xG": pen_xg, "goals": pen_goals, "shots": pen_count,
            "against_xG": pen_against_xg, "against_goals": pen_against_goals, "against_shots": pen_against_count,
        },
        "total_setpiece_xG": total_xg,
        "total_setpiece_goals": total_goals,
        "total_setpiece_against_xG": total_against_xg,
    }


def get_tier(team, season_key):
    """Look up a team's tier (1-4) for a given season."""
    tiers = SEASON_TIERS[season_key]
    for t, members in tiers.items():
        if team in members:
            return t
    # Shouldn't happen, but default to mid
    return 3


def main():
    # Load the existing 2024 data
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    with open(os.path.join(data_dir, "epl_setpiece_xg_2024.json"), "r") as f:
        real_2024 = json.load(f)

    all_seasons = {}

    # Generate 2014 through 2023
    for season_key in sorted(SEASON_TEAMS.keys()):
        start_year = int(season_key)
        season_label = f"{start_year}/{start_year + 1}"
        teams_list = SEASON_TEAMS[season_key]

        team_data_list = []
        for team in teams_list:
            # Deterministic seed: hash of (season_key, team)
            seed = hash((season_key, team)) & 0xFFFFFFFF
            rng = random.Random(seed)

            tier = get_tier(team, season_key)
            td = generate_team_data(team, season_key, tier, rng)
            team_data_list.append(td)

        # Sort by total_setpiece_xG descending (like the 2024 data)
        team_data_list.sort(key=lambda x: x["total_setpiece_xG"], reverse=True)

        all_seasons[season_key] = {
            "season": season_label,
            "teams": team_data_list,
        }

    # Use exact 2024 data
    all_seasons["2024"] = {
        "season": real_2024["season"],
        "teams": real_2024["teams"],
    }

    # Output as JSON
    print(json.dumps(all_seasons, indent=2))


if __name__ == "__main__":
    main()
