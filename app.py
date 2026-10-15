from flask import Flask, render_template, request
from main import processSeason, prepareData, trainFinalModel, predictMatch, seasons, trainingData, teams
from datetime import datetime
from urllib.request import urlopen
from pathlib import Path

def updateMatchData():
    url = "https://www.football-data.co.uk/mmz4281/2627/E0.csv"
    filePath = Path(__file__).parent / "PL2627.csv"

    try:
        with urlopen(url, timeout=10) as response:
            data = response.read()
        if b"HomeTeam" not in data[:500] or b"AwayTeam" not in data[:500]:
            raise ValueError("Unexpected CSV format")
        filePath.write_bytes(data)
        print("Match data updated successfully.")

    except Exception as error:
        print(f"Update failed: {error}")
        print("Using existing match data.")

updateMatchData()

app = Flask(__name__)

for season in seasons:
    processSeason(season)


X,Y = prepareData(trainingData)
finalModel, finalScaler = trainFinalModel(X, Y)

@app.route("/", methods=["GET", "POST"])
def home():
    teamList = sorted([
        team for team in teams
        if teams[team]["games"] > 0
    ])

    if request.method == "POST":
        homeTeam = request.form["homeTeam"]
        awayTeam = request.form["awayTeam"]
        dateInput = request.form["matchDate"]

        if homeTeam == awayTeam:
            return render_template(
                "index.html",
                teams=teamList,
                error="Home and away teams must be different",
                selectedHome=homeTeam,
                selectedAway=awayTeam,
                selectedDate=dateInput
            )

        matchDate = datetime.strptime(dateInput, "%Y-%m-%d")

        prediction = predictMatch(
            homeTeam,
            awayTeam,
            matchDate,
            finalModel,
            finalScaler
        )

        if prediction is None:
            return render_template(
                "index.html",
                teams=teamList,
                error="Match date must be after both teams' most recent match.",
                selectedHome=homeTeam,
                selectedAway=awayTeam,
                selectedDate=dateInput
            )
    
    return render_template(
        "index.html", 
        teams=teamList,
        prediction=prediction if request.method == "POST" else None,
        selectedHome=homeTeam if request.method == "POST" else None,
        selectedAway=awayTeam if request.method == "POST" else None,
        selectedDate=dateInput if request.method == "POST" else None
    )

if __name__ == "__main__":
    app.run(debug=True)