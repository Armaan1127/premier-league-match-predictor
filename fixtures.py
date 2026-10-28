import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
from functools import lru_cache
from zoneinfo import ZoneInfo

load_dotenv()

TEAM_NAMES = {
    "Arsenal FC": "Arsenal",
    "Aston Villa FC": "Aston Villa",
    "AFC Bournemouth": "Bournemouth",
    "Brentford FC": "Brentford",
    "Brighton & Hove Albion FC": "Brighton",
    "Burnley FC": "Burnley",
    "Chelsea FC": "Chelsea",
    "Coventry City FC": "Coventry",
    "Crystal Palace FC": "Crystal Palace",
    "Everton FC": "Everton",
    "Fulham FC": "Fulham",
    "Hull City AFC": "Hull",
    "Ipswich Town FC": "Ipswich",
    "Leeds United FC": "Leeds",
    "Liverpool FC": "Liverpool",
    "Manchester City FC": "Man City",
    "Manchester United FC": "Man United",
    "Newcastle United FC": "Newcastle",
    "Nottingham Forest FC": "Nott'm Forest",
    "Sunderland AFC": "Sunderland",
    "Tottenham Hotspur FC": "Tottenham",
    "West Ham United FC": "West Ham",
    "Wolverhampton Wanderers FC": "Wolves",
}


@lru_cache(maxsize=1)
def fetchFixtures():
    apiKey = os.getenv("FOOTBALL_API_KEY")

    if not apiKey:
        raise RuntimeError("FOOTBALL_API_KEY is missing")

    response = requests.get(
        "https://api.football-data.org/v4/competitions/PL/matches",
        headers={"X-Auth-Token": apiKey},
        params={"status": "SCHEDULED"},
        timeout=10
    )

    response.raise_for_status()

    fixtures = []

    for match in response.json()["matches"]:
        homeName = match["homeTeam"]["name"]
        awayName = match["awayTeam"]["name"]

        if homeName not in TEAM_NAMES or awayName not in TEAM_NAMES:
            print(f"Unknown team: {homeName} / {awayName}")
            continue

        matchDate = datetime.fromisoformat(
            match["utcDate"].replace("Z", "+00:00")
        )

        if matchDate <= datetime.now(timezone.utc):
            continue

        fixtures.append({
            "id": match["id"],
            "homeTeam": TEAM_NAMES[homeName],
            "awayTeam": TEAM_NAMES[awayName],
            "homeCrest": match["homeTeam"].get("crest"),
            "awayCrest": match["awayTeam"].get("crest"),
            "date": matchDate,
            "localDate": matchDate.astimezone(ZoneInfo("America/New_York")),
            "matchday": match.get("matchday"),
        })

    fixtures.sort(key=lambda match: match["date"])

    matchdays = []
    for fixture in fixtures:
        if fixture["matchday"] not in matchdays:
            matchdays.append(fixture["matchday"])

        if len(matchdays) > 2:
            break

    return [
        fixture for fixture in fixtures
        if fixture["matchday"] in matchdays[:2]
    ]

from time import monotonic

_cached_fixtures = None
_cache_time = 0

def getUpcomingFixtures():
    global _cached_fixtures, _cache_time

    now = monotonic()

    if _cached_fixtures is None or now - _cache_time >= 1800:
        _cached_fixtures = fetchFixtures()
        _cache_time = now

    return _cached_fixtures

if __name__ == "__main__":
    for fixture in getUpcomingFixtures():
        print(
            fixture["matchday"],
            fixture["homeTeam"],
            "vs",
            fixture["awayTeam"],
            fixture["date"]
        )