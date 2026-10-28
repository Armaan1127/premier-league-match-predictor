from flask import Flask, render_template, request
from main import (
    processSeason,
    prepareData,
    trainFinalModel,
    predictMatch,
    seasons,
    trainingData,
    refreshCurrentSeason
)
from datetime import datetime, timedelta
from urllib.request import urlopen
from pathlib import Path
from threading import Lock
from fixtures import getUpcomingFixtures

app = Flask(__name__)

MATCH_DATA_URL = "https://www.football-data.co.uk/mmz4281/2627/E0.csv"
MATCH_DATA_FILE = Path(__file__).parent / "PL2627.csv"

REFRESH_INTERVAL = timedelta(minutes=30)

refreshLock = Lock()
lastRefresh = None


def updateMatchData():
    try:
        with urlopen(MATCH_DATA_URL, timeout=10) as response:
            data = response.read()

        if b"HomeTeam" not in data[:500] or b"AwayTeam" not in data[:500]:
            raise ValueError("Unexpected CSV format")

        existingData = (
            MATCH_DATA_FILE.read_bytes()
            if MATCH_DATA_FILE.exists()
            else None
        )

        if data == existingData:
            return False

        MATCH_DATA_FILE.write_bytes(data)

        print("New match data downloaded.")
        return True

    except Exception as error:
        print(f"Match data update failed: {error}")
        return False


# Download latest results before initial processing.
updateMatchData()

for season in seasons:
    processSeason(season)

X, Y = prepareData(trainingData)
finalModel, finalScaler = trainFinalModel(X, Y)

lastRefresh = datetime.now()


def refreshIfNeeded():
    global lastRefresh

    with refreshLock:
        now = datetime.now()

        if now - lastRefresh < REFRESH_INTERVAL:
            return

        lastRefresh = now

        if updateMatchData():
            refreshCurrentSeason()
            print("Team statistics refreshed successfully.")


@app.route("/", methods=["GET", "POST"])
def home():
    fixtures = []
    fixtureError = None
    prediction = None
    selectedFixture = None
    error = None

    refreshIfNeeded()

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

            with refreshLock:
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