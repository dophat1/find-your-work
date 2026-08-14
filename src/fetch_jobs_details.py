import base64
import json
import requests
import db_connect

BASE_URL = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobdetails/" 
HEADERS = {
    "X-API-Key": "jobboerse-jobsuche",
    "Origin": "https://www.arbeitsagentur.de",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
}

def encoding_referenznummer(refnr):
    enc_refnr = refnr.encode()
    base64_enc_refnr = base64.b64encode(enc_refnr)
    dec_refnr = base64_enc_refnr.decode()
    return dec_refnr

def get_job_detail(refnr):
    response = requests.get(f"{BASE_URL}{encoding_referenznummer(refnr)}", headers=HEADERS)
    result = response.json()
    job_description = result['stellenangebotsBeschreibung']
    return job_description

def update_job_detail(conn, refnr, source, raw_description_text):
    update_query = 'UPDATE postings SET raw_description_text = ? WHERE source = ? AND referenznummer = ?;'
    params = (raw_description_text, source, refnr)
    conn.execute(update_query, params)
    conn.commit()
    

def run_fetch_jobs_details(conn):
    work_list_query = 'SELECT source, referenznummer FROM postings WHERE raw_description_text IS NULL;'
    work_list = conn.execute(work_list_query).fetchall()
    for source, referenznummer in work_list:
        try:
            job_description = get_job_detail(referenznummer)
            update_job_detail(conn, referenznummer, source, job_description)
        except Exception as e:
            print(f"There is problem fetching data from reference number {referenznummer} fron {source}. {e} occurs.")
            continue

if __name__ == "__main__":
    conn = db_connect.get_connection()
    run_fetch_jobs_details(conn)