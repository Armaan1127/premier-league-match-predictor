import csv
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

teams = {}
trainingData = []

seasons = [
    "PL2122.csv",
    "PL2223.csv",
    "PL2324.csv",
    "PL2425.csv",
    "PL2526.csv",
    "PL2627.csv"
]

def createTeam():
    return {
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "games": 0,
        "goals_for": 0,
        "goals_against": 0,
        "home_games": 0,
        "away_games": 0,
        "home_wins": 0,
        "away_wins": 0,
        "home_goals_for": 0,
        "home_goals_against": 0,
        "away_goals_for": 0,
        "away_goals_against": 0,
        "results": [],
        "elo": 1500,
        "last_match_date": None,
        "SOTfor": 0,
        "SOTagainst": 0,
        "homeSOT": 0,
        "awaySOT": 0
    }

def resetSeasonStats(team):
    team["wins"]= 0
    team["draws"]= 0
    team["losses"]= 0
    team["games"]= 0
    team["goals_for"]= 0
    team["goals_against"]= 0
    team["home_games"]= 0
    team["away_games"]= 0
    team["home_wins"]= 0
    team["away_wins"]= 0
    team["home_goals_for"]= 0
    team["home_goals_against"]= 0
    team["away_goals_for"]= 0
    team["away_goals_against"]= 0
    team["results"]= []
    team["SOTfor"]= 0
    team["SOTagainst"]= 0
    team["homeSOT"]= 0
    team["awaySOT"]= 0

def calculateFormPoints(results):
    formPoints = 0

    for i, result in enumerate(results[-5:]):
        weight = i + 1

        if result == "W":
            formPoints += 3 * weight
        elif result == "D":
            formPoints += weight

    return formPoints

def updateElo(home, away, result):
    homeAdvantage = 75

    #elo formula
    expectedHome = 1 / (1 + (10 ** ((teams[away]["elo"] - (teams[home]["elo"] + homeAdvantage)) / 400)))
    expectedAway = 1 - expectedHome

    if result == "H":
        actualHome, actualAway = 1, 0
    elif result == "D":
        actualHome, actualAway = 0.5, 0.5
    else:
        actualHome, actualAway = 0,1

    #elo change formula, k controls much ratings change
    k = 50

    teams[home]["elo"] += k * (actualHome - expectedHome)
    teams[away]["elo"] += k * (actualAway - expectedAway)

def updateTeamStats(home, away, homeGoals, awayGoals, homeSOT, awaySOT, matchDate, result):
    teams[home]["games"] += 1
    teams[away]["games"] += 1

    teams[home]["goals_for"] += homeGoals
    teams[home]["goals_against"] += awayGoals

    teams[away]["goals_for"] += awayGoals
    teams[away]["goals_against"] += homeGoals

    teams[home]["home_games"] += 1
    teams[away]["away_games"] += 1

    teams[home]["home_goals_for"] += homeGoals
    teams[home]["home_goals_against"] += awayGoals

    teams[away]["away_goals_for"] += awayGoals
    teams[away]["away_goals_against"] += homeGoals

    teams[home]["last_match_date"] = matchDate
    teams[away]["last_match_date"] = matchDate

    teams[home]["SOTfor"] += homeSOT
    teams[home]["SOTagainst"] += awaySOT
    teams[home]["homeSOT"] += homeSOT
    
    teams[away]["SOTfor"] += awaySOT
    teams[away]["SOTagainst"] += homeSOT
    teams[away]["awaySOT"] += awaySOT

    if result == "H":
        teams[home]["wins"] += 1
        teams[away]["losses"] += 1
        teams[home]['home_wins'] += 1
        teams[home]["results"].append("W")
        teams[away]["results"].append("L")

    elif result == "D":
        teams[home]["draws"] += 1
        teams[away]["draws"] += 1
        teams[home]["results"].append("D")
        teams[away]["results"].append("D")
            

    elif result == "A":
        teams[home]["losses"] += 1
        teams[away]["wins"] += 1
        teams[away]['away_wins'] += 1
        teams[away]["results"].append("W")
        teams[home]["results"].append("L")
    
def calculateFeatures(home, away, matchDate):
    homePPG = (3 * teams[home]["wins"] + teams[home]["draws"]) / teams[home]["games"]
    awayPPG = (3 * teams[away]["wins"] + teams[away]["draws"]) / teams[away]["games"]

    homeGD = (teams[home]["goals_for"] - teams[home]["goals_against"]) / teams[home]["games"]
    awayGD = (teams[away]["goals_for"] - teams[away]["goals_against"]) / teams[away]["games"]

    homeGDVenue = (teams[home]["home_goals_for"] - teams[home]["home_goals_against"]) / teams[home]["home_games"]
    awayGDVenue = (teams[away]["away_goals_for"] - teams[away]["away_goals_against"]) / teams[away]["away_games"]

    homeSOTFor = teams[home]["homeSOT"] / teams[home]["home_games"]
    awaySOTFor = teams[away]["awaySOT"] / teams[away]["away_games"]

    homeSOTAgainst = teams[home]["SOTagainst"] / teams[home]["games"]
    awaySOTAgainst = teams[away]["SOTagainst"] / teams[away]["games"]

    homeFormPoints = calculateFormPoints(teams[home]["results"])
    awayFormPoints = calculateFormPoints(teams[away]["results"])

    homeRestDays = (matchDate - teams[home]["last_match_date"]).days
    awayRestDays = (matchDate - teams[away]["last_match_date"]).days

    return [
        teams[home]["home_goals_for"] / teams[home]["home_games"],
        teams[away]["away_goals_for"] / teams[away]["away_games"],
        teams[home]["home_goals_against"] / teams[home]["home_games"],
        teams[away]["away_goals_against"] / teams[away]["away_games"],
        teams[home]["home_wins"] / teams[home]["home_games"],
        teams[away]["away_wins"] / teams[away]["away_games"],
        homeFormPoints,
        awayFormPoints,
        homePPG,
        awayPPG,
        teams[home]["elo"],
        teams[away]["elo"],
        homeRestDays,
        awayRestDays,
        homeSOTFor,
        awaySOTFor,
        homeSOTAgainst,
        awaySOTAgainst,
        homeGD,
        awayGD,
        homeGDVenue,
        awayGDVenue
    ]

def processSeason(season):
    for team in teams:
        resetSeasonStats(teams[team])

    with open(BASE_DIR / season) as source:
        data = csv.DictReader(source)
            
        for match in data:
            hTeam = match["HomeTeam"]
            aTeam = match["AwayTeam"]
            result = match["FTR"]
            hGoals = int(match["FTHG"])
            aGoals = int(match["FTAG"])
            matchDate = datetime.strptime(match["Date"], "%d/%m/%Y")
            hShotsTarget = int(match["HST"])
            aShotsTarget = int(match["AST"])

            if hTeam not in teams:
                teams[hTeam] = createTeam()
                                    
            if aTeam not in teams:
                teams[aTeam] = createTeam()

            if season != "PL2627.csv" and teams[hTeam]["home_games"] != 0 and teams[aTeam]["away_games"] != 0:
                #TRAINING ROW
                features = calculateFeatures(hTeam, aTeam, matchDate)
                
                trainingData.append({
                    "features": features,
                    "result": result,
                    "season": season
                })

            updateElo(hTeam, aTeam, result)
            
            updateTeamStats(
                hTeam,
                aTeam,
                hGoals,
                aGoals,
                hShotsTarget,
                aShotsTarget,
                matchDate,
                result
            )

def prepareData(trainingData):
    X = []
    Y = []

    for row in trainingData:
        X.append(row["features"])
        Y.append(row["result"])

    return X, Y

def trainFinalModel(X, Y):
    finalScaler = StandardScaler()
    X_final = finalScaler.fit_transform(X)

    finalModel = LogisticRegression(max_iter = 1000)
    finalModel.fit(X_final, Y)

    return finalModel, finalScaler

def findTeam(teamInput):
    teamInput = teamInput.strip().lower()

    for team in teams:
        if team.lower() == teamInput:
            return team

    aliases = {
        "manchester city": "Man City",
        "manchester united": "Man United",
        "manchester utd": "Man United",
        "man utd": "Man United",
        "man u": "Man United",
        "tottenham hotspurs": "Tottenham",
        "tottenham hotspur": "Tottenham",
        "tottenham spurs": "Tottenham",
        "spurs": "Tottenham",
        "nottingham forest": "Nott'm Forest",
        "nottingham": "Nott'm Forest"
    }
    
    if teamInput in aliases:
        return aliases[teamInput]

    return None

def predictMatch(home, away, matchDate, finalModel, finalScaler):
    if home not in teams or away not in teams:
        print("Team not found.")
        return

    if teams[home]["home_games"] == 0 or teams[away]["away_games"] == 0:
        print("Not enough current-season data for this matchup.")
        return

    homeRestDays = (matchDate - teams[home]["last_match_date"]).days
    awayRestDays = (matchDate - teams[away]["last_match_date"]).days

    if homeRestDays <= 0 or awayRestDays <= 0:
        return None

    features = calculateFeatures(home, away, matchDate)

    scaledFeatures = finalScaler.transform([features])

    probabilities = finalModel.predict_proba(scaledFeatures)[0]

    probabilityMap = dict(zip(finalModel.classes_, probabilities))

    return {
        "home": probabilityMap["H"],
        "draw": probabilityMap["D"],
        "away": probabilityMap["A"]
    }

def main():
    for season in seasons:
        processSeason(season)

    X, Y = prepareData(trainingData)
    finalModel, finalScaler = trainFinalModel(X, Y)
    
    #home team
    home = findTeam(input("Home team: "))

    #check if home team is valid NOT CASE SENSITIVE
    if home is None or teams[home]["games"] == 0:
        print("Invalid home team.")
        exit()

    #away team
    away = findTeam(input("Away team: "))

    #check if away team is valid NOT CASE SENSITIVE
    if away is None or teams[away]["games"] == 0:
        print("Invalid away team.")
        exit()

    if home == away:
        print("Home and away teams must be different")
        exit()

    dateInput = input("Match date (DD/MM/YYYY): ")

    try:
        matchDate = datetime.strptime(dateInput, "%d/%m/%Y")
    except ValueError:
        print("Invalid date. Use DD/MM/YYYY.")
        exit()

    prediction = predictMatch(home, away, matchDate, finalModel, finalScaler)

    if prediction:
        print(f"\n{home} vs {away}")
        print(f"{home} win: {prediction['home']:.1%}")
        print(f"Draw: {prediction['draw']:.1%}")
        print(f"{away} win: {prediction['away']:.1%}")

if __name__ == "__main__":
    main()