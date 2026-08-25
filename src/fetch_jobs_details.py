import base64
import time
import requests
import db_connect

BASE_URL = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobdetails/"
HEADERS = {
    "X-API-Key": "jobboerse-jobsuche",
    "Origin": "https://www.arbeitsagentur.de",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
}

# Small delay between requests so we don't hammer an undocumented API.
REQUEST_DELAY_SECONDS = 0.5

# Marks a posting we tried and permanently couldn't fetch a description for
# (removed listing, no description field, etc.) so future runs don't keep
# re-requesting it forever.
UNAVAILABLE_MARKER = "__UNAVAILABLE__"


def encoding_referenznummer(refnr):
    enc_refnr = refnr.encode()
    base64_enc_refnr = base64.b64encode(enc_refnr)
    dec_refnr = base64_enc_refnr.decode()
    return dec_refnr

def get_job_detail(refnr):
    response = requests.get(f"{BASE_URL}{encoding_referenznummer(refnr)}", headers=HEADERS)
    if response.status_code != 200:
        raise ValueError(f"BA API returned {response.status_code} for {refnr}")
    result = response.json()
    # Not every posting has a description (removed/expired listings still
    # show up in search but 404/empty on the detail endpoint) - treat a
    # missing field as "no description available" instead of crashing.
    job_description = result.get('stellenangebotsBeschreibung')
    if not job_description:
        raise KeyError(f"stellenangebotsBeschreibung missing for {refnr}")
    return job_description

def update_job_detail(conn, refnr, source, raw_description_text):
    update_query = 'UPDATE postings SET raw_description_text = ? WHERE source = ? AND referenznummer = ?;'
    params = (raw_description_text, source, refnr)
    conn.execute(update_query, params)
    conn.commit()


def run_fetch_jobs_details(conn):
    work_list_query = 'SELECT source, referenznummer FROM postings WHERE raw_description_text IS NULL;'
    work_list = conn.execute(work_list_query).fetchall()
    fetched = 0
    unavailable = 0
    for source, referenznummer in work_list:
        try:
            job_description = get_job_detail(referenznummer)
            update_job_detail(conn, referenznummer, source, job_description)
            fetched += 1
        except Exception as e:
            # Mark it so this run (and future runs) don't retry it forever -
            # it stays excluded from skill/German-level extraction, same as
            # any other posting with no usable description.
            print(f"There is problem fetching data from reference number {referenznummer} fron {source}. {e} occurs.")
            update_job_detail(conn, referenznummer, source, UNAVAILABLE_MARKER)
            unavailable += 1
        time.sleep(REQUEST_DELAY_SECONDS)
    print(f"Fetched {fetched} descriptions, {unavailable} permanently unavailable, out of {len(work_list)} pending.")

if __name__ == "__main__":
    conn = db_connect.get_connection()
    run_fetch_jobs_details(conn)
