# Premier League Match Predictor

**Live Demo:** https://premier-league-match-predictor-lbsy.onrender.com

A machine learning web application that predicts the probabilities of Premier League matches ending in a home win, draw, or away win.

Built with **Python, Flask, and scikit-learn**, the application combines historical match data, current-season team statistics, and live Premier League fixtures to generate predictions through an interactive web interface.

## Features

### Web Application

- Displays upcoming Premier League fixtures for the next two matchdays.
- Retrieves fixtures, kickoff times, and team badges using the football-data.org API.
- Generates home win, draw, and away win probabilities with one click.
- Visualizes predictions using probability bars.
- Responsive interface with Premier League-inspired styling.
- Automatically removes fixtures that have already started.

### Machine Learning

The model uses **22 pre-match features**, including:

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

### Automatic Data Updates

- Downloads the latest current-season match results from Football-Data.co.uk.
- Checks for updated match results every 30 minutes when the application receives traffic.
- Rebuilds current-season team statistics when new results become available.
- Preserves the trained historical model without unnecessary retraining.
- Caches upcoming fixtures for 30 minutes to reduce API requests.
- Uses previously cached fixtures if the fixture API temporarily becomes unavailable.

## Model & Evaluation

The predictor uses **multinomial logistic regression** with standardized features.

Historical data was split chronologically, using the first 80% of matches for training and the final 20% for testing. This approach better simulates predicting future matches using past data compared with a random split.

### Evaluation Results

| Metric | Result |
|---|---|
| Log Loss | 1.0186 |
| Accuracy | 50.83% |

After evaluation, the final model is trained on all available historical matches before generating current-season predictions.

## Data Sources

### Football-Data.co.uk

- Historical Premier League match results from 2021/22 through 2025/26.
- Current-season results for 2026/27.
- Match statistics including goals, shots on target, results, and dates.

### football-data.org API

- Upcoming Premier League fixtures.
- Team names and badges.
- Match dates, kickoff times, and matchday information.

Historical seasons are used to train the machine learning model. Current-season results are used to maintain up-to-date team statistics and are excluded from model training.

## Tech Stack

| Component | Technology |
|---|---|
| Backend | Python, Flask |
| Machine Learning | scikit-learn, Logistic Regression, StandardScaler |
| Frontend | HTML, CSS, Jinja2 |
| API Integration | football-data.org |
| Data Processing | Python CSV module |
| Deployment | Render, Gunicorn |

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/Armaan1127/premier-league-match-predictor.git
cd premier-league-match-predictor
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the API key

Create a `.env` file in the project directory:

```env
FOOTBALL_API_KEY=your_api_key_here
```

Obtain a free API key from https://www.football-data.org/.

The `.env` file is excluded from version control to protect the API key.

### 4. Start the web application

```bash
python3 app.py
```

Open http://127.0.0.1:5000 in your browser.

Select an upcoming fixture and click **Predict** to view the model's probabilities.

### Command-Line Version

The predictor can also be used directly from the terminal:

```bash
python3 main.py
```

Example output:

```text
Home team: everton
Away team: liverpool
Match date (DD/MM/YYYY): 29/11/2026

Everton vs Liverpool
Everton win: 18.2%
Draw: 16.4%
Liverpool win: 65.3%
```

*The example illustrates the command-line output format. Actual probabilities depend on the available match data.*

## Project Structure

```text
premier-league-match-predictor/
|-- app.py
|-- main.py
|-- fixtures.py
|-- requirements.txt
|-- README.md
|-- .gitignore
|-- PL2122.csv
|-- PL2223.csv
|-- PL2324.csv
|-- PL2425.csv
|-- PL2526.csv
|-- PL2627.csv
|-- templates/
|   `-- index.html
`-- static/
    `-- style.css
```

### File Descriptions

- `app.py` - Flask application, prediction routes, and automatic match-data refresh.
- `main.py` - Match processing, feature engineering, Elo ratings, model training, and prediction logic.
- `fixtures.py` - Football API integration, fixture caching, and matchday selection.
- `PL2122.csv`-`PL2526.csv` - Historical training data.
- `PL2627.csv` - Current-season match results.
- `templates/` - HTML/Jinja2 templates.
- `static/` - CSS styling.

## Deployment

The application is deployed on **Render** using **Gunicorn**.

The `FOOTBALL_API_KEY` environment variable is configured securely in Render rather than stored in the repository.

**Live Application:** https://premier-league-match-predictor-lbsy.onrender.com