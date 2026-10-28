from flask import Flask, render_template, request
from main import processSeason, prepareData, trainFinalModel, predictMatch, seasons, trainingData, teams
from datetime import datetime
from urllib.request import urlopen
from pathlib import Path
from fixtures import getUpcomingFixtures

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
    fixtures = []
    fixtureError = None
    prediction = None
    selectedFixture = None
    error = None

    try:
        fixtures = getUpcomingFixtures()
    except Exception as exception:
        print(f"Fixture API error: {exception}")
        fixtureError = "Upcoming fixtures are temporarily unavailable."

    if request.method == "POST":
        fixtureId = request.form.get("fixtureId")

        selectedFixture = next(
            (
                fixture for fixture in fixtures
                if str(fixture["id"]) == fixtureId
            ),
            None
        )

        if selectedFixture is None:
            error = "Please select a valid upcoming fixture."
        else:
            matchDate = selectedFixture["date"].replace(tzinfo=None)

            prediction = predictMatch(
                selectedFixture["homeTeam"],
                selectedFixture["awayTeam"],
                matchDate,
                finalModel,
                finalScaler
            )

            if prediction is None:
                error = "Unable to predict this match with the available data."

    return render_template(
        "index.html",
        fixtures=fixtures,
        prediction=prediction,
        selectedFixture=selectedFixture,
        fixtureError=fixtureError,
        error=error
    )

if __name__ == "__main__":
    app.run(debug=True)