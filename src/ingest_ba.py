# src/ingest_ba.py
import time
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

# Small delay between requests so we don't hammer an undocumented,
# reverse-engineered API - be a good citizen, avoid getting IP-blocked.
REQUEST_DELAY_SECONDS = 0.5
PAGE_SIZE = 100

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

# Edit this list to change where/what this pipeline searches for.
# 'wo' = city/location, 'was' = keyword, 'umkreis' = radius in km,
# 'angebotsart' = None (all) or 34 (internships/working student, per BA's own codes).
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


def fetch_jobs(was: str, wo: str, umkreis: int, angebotsart: str = None, size: int = PAGE_SIZE, page: int = 1) -> dict:
    """
    Query the BA Jobsuche API, return parsed JSON. Raises ValueError on non-200 response.
    """
    # Build a params dict from the args (only include angebotsart if it's not None)
    params = {
        'was': was,
        'wo': wo,
        'umkreis': umkreis,
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


def fetch_all_pages(was: str, wo: str, umkreis: int, angebotsart: str = None) -> list[dict]:
    """
    Page through the BA Jobsuche API until we've collected every result for
    this query (or the API stops returning new postings). The API caps
    'size' at 100 per page, so a single fetch_jobs() call silently drops
    anything past the first 100 matches - this walks all pages instead.
    """
    all_pages = []
    page = 1
    while True:
        data = fetch_jobs(was=was, wo=wo, umkreis=umkreis, angebotsart=angebotsart, size=PAGE_SIZE, page=page)
        all_pages.append(data)
        results = data.get('ergebnisliste', [])
        max_results = data.get('maxErgebnisse', len(results))
        fetched_so_far = page * PAGE_SIZE
        if len(results) < PAGE_SIZE or fetched_so_far >= max_results:
            break
        page += 1
        time.sleep(REQUEST_DELAY_SECONDS)
    return all_pages


def save_raw(data: dict, tag: str) -> Path:
    """
    Saved data into data/raw/
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)


    utc_timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    filename = f"ba_{tag}_{utc_timestamp}.json"

    filepath = RAW_DIR/filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return filepath

def run_ingestion():
    """
    Run the ingestion and saved data, paging through every query's full result set.
    """
    success = 0
    failed = []
    total_pages_saved = 0

    for query in QUERIES:
        try:
            pages = fetch_all_pages(**query)
            tag = f"{query['wo']}_{query['was']}".replace(' ', '_').lower()
            for i, page_data in enumerate(pages):
                page_tag = tag if i == 0 else f"{tag}_p{i + 1}"
                save_raw(page_data, page_tag)
                total_pages_saved += 1
            success += 1
        except (ValueError, requests.exceptions.RequestException) as e:
            failed.append((query, e))
            print(f"There is {e} on {query}")
        time.sleep(REQUEST_DELAY_SECONDS)

    print(f"{success}/{len(QUERIES)} queries succeeded, {total_pages_saved} page(s) saved")
    for query, err in failed:
        print(f"Query {query} failed with {err}")

if __name__ == "__main__":

    run_ingestion()
