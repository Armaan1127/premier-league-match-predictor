import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = "https://api.football-data.org/v4/competitions/PL/matches"

headers = {
    "X-Auth-Token": os.getenv("FOOTBALL_API_KEY")
}

params = {
    "status": "SCHEDULED"
}

response = requests.get(
    url,
    headers=headers,
    params=params,
    timeout=10
)

print("Status code:", response.status_code)
print("Response:", response.text)
print("API key loaded:", bool(os.getenv("FOOTBALL_API_KEY")))

response.raise_for_status()
matches = response.json()["matches"]

for match in matches[:10]:
    print(
        match["utcDate"],
        match["homeTeam"]["name"],
        "vs",
        match["awayTeam"]["name"]
    )