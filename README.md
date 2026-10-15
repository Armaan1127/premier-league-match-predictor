# Premier League Match Predictor
**Live Demo:** https://premier-league-match-predictor-lbsy.onrender.com

A machine learning project that predicts the probabilities of a Premier League match ending in a home win, draw, or away win.

The model is built in Python using historical Premier League match data and logistic regression. It uses pre-match team statistics including form, Elo ratings, goals, shots on target, points per game, and rest days to generate outcome probabilities.

## Features

The model uses 22 pre-match features:

- Home and away goals scored per game
- Home and away goals conceded per game
- Home and away win rates
- Recent form, weighted toward more recent matches
- Points per game
- Elo ratings
- Rest days since each team's previous match
- Shots on target for and against
- Overall goal difference per game
- Home- and away-specific goal difference per game

All features are calculated using only information available before the match being predicted, preventing data leakage.

## Model & Evaluation

The predictor uses multinomial logistic regression with standardized features.

To evaluate the model, the historical data was split chronologically, using the first 80% of matches for training and the final 20% for testing. A chronological split was used instead of a random split to better simulate predicting future matches from past data.

Evaluation results:
- Log loss: 1.0186
- Accuracy: 50.83%

After evaluation, the final model is trained on all available historical matches before generating current-season predictions.

## Data

Match data comes from Football-Data.co.uk and covers Premier League seasons from 2021/22 through 2026/27.

Historical seasons from 2021/22 through 2025/26 are used to train the model. The 2026/27 season is used to maintain the current team statistics for predictions and is excluded from the training data. The current-season CSV is automatically refreshed from Football-Data.co.uk when the application starts.

The dataset includes match results, goals, shots on target, and match dates.

## How to run

- Install the required dependencies:

```bash
pip install -r requirements.txt
```

- Run the predictor:

```bash
python3 main.py
```

- Enter the home team, away team, and match date when prompted

```text
Home team: everton
Away team: liverpool
Match date (DD/MM/YYYY): 29/11/2026

Everton vs Liverpool
Everton win: 18.2%
Draw: 16.4%
Liverpool win: 65.3%
```

## Project Structure

- `main.py` - processes match data, calculates team statistics and features, trains the model, and generates predictions

- `PL2122.csv`–`PL2526.csv` — historical training data

- `PL2627.csv` — current-season data used to build current team statistics

- `README.md` — project documentation

- `app.py` — Flask web application for generating predictions through a browser

- `templates/` — HTML templates for the web interface

- `static/` — CSS styling for the web interface