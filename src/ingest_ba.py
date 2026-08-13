# src/ingest_ba.py
import requests
import json
from datetime import datetime, timezone
from pathlib import Path


# HEADERS = {
#     'User-Agent': 'Jobsuche/2.9.2 (de.arbeitsagentur.jobboerse; build:1077; iOS 15.1.0) Alamofire/5.4.4',
#     'Host': 'rest.arbeitsagentur.de',
#     'X-API-Key': 'jobboerse-jobsuche',
#     'Connection': 'keep-alive',
# }

BASE_URL = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v6/jobs" 
HEADERS = {
    "X-API-Key": "jobboerse-jobsuche",
    "Origin": "https://www.arbeitsagentur.de",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
}


RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

QUERIES = [
    {"wo": "Augsburg", "umkreis": 30, "was": "Data", "angebotsart": None},
    {"wo": "Augsburg", "umkreis": 30, "was": "ML", "angebotsart": None},
    {"wo": "Augsburg", "umkreis": 30, "was": "Analytics", "angebotsart": None},
    {"wo": "Augsburg", "umkreis": 30, "was": "Data", "angebotsart": 34},
    {"wo": "Augsburg", "umkreis": 30, "was": "ML", "angebotsart": 34},
    {"wo": "Augsburg", "umkreis": 30, "was": "Analytics", "angebotsart": 34},
    {"wo": "Munchen", "umkreis": 30, "was": "Data", "angebotsart": None},
    {"wo": "Munchen", "umkreis": 30, "was": "ML", "angebotsart": None},
    {"wo": "Munchen", "umkreis": 30, "was": "Analytics", "angebotsart": None},
    {"wo": "Munchen", "umkreis": 30, "was": "Data", "angebotsart": 34},
    {"wo": "Munchen", "umkreis": 30, "was": "ML", "angebotsart": 34},
    {"wo": "Munchen", "umkreis": 30, "was": "Analytics", "angebotsart": 34}
]


def fetch_jobs(was: str, wo: str, umkreis: int, angebotsart: str = None, size: int = 100, page: int = 1) -> dict:
    """
    Query the BA Jobsuche API, return parsed JSON. Raises ValueError on non-200 response.
    """
    # Build a params dict from the args (only include angebotsart if it's not None)
    params = {
        'was':was,
        'wo': wo,
        'umkreis':umkreis,
        'size': size,
        'page': page
    }
    if angebotsart is not None:
        params['angebotsart'] = angebotsart
    
    response = requests.get(BASE_URL, headers=HEADERS, params=params)

    if response.status_code != 200: 
        raise ValueError(f"BA API returned {response.status_code}: {response.text}")
    else:
        return response.json()


def save_raw(data: dict, tag: str) -> Path:
    """
    Saved data into data/raw/
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    
    
    utc_timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    filename = f"ba_{tag}_{utc_timestamp}.json"
    
    filepath = RAW_DIR/filename
    
    with open(filepath, 'w') as f: 
        json.dump(data, f, indent=2, ensure_ascii=False)

    return filepath 

def run_ingestion():
    """
    Run the ingestion and saved data. 
    """
    success = 0
    failed = []

    for query in QUERIES:
        try:
            data = fetch_jobs(**query)
            tag = f"{query['wo']}_{query['was']}".replace(' ', '_').lower()
            save_raw(data, tag)
            success += 1
        except (ValueError, requests.exceptions.RequestException) as e:
            failed.append((query, e))
            print(f"There is {e} on {query}")

    print(f"{success}/{len(QUERIES)} succeeded")
    for query, err in failed:
        print(f"Query {query} failed with {err}")

if __name__ == "__main__":
   
    run_ingestion()