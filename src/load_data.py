import sqlite3
import db_connect
from pathlib import Path
from urllib.parse import quote
import json

def get_or_insert_company(conn, name):
    query = 'SELECT company_id FROM companies WHERE name = ?'
    result = conn.execute(query, (name,)).fetchone()
    if result is not None:
        return result[0]
    else:
        add_query = 'INSERT INTO companies (name) VALUES (?)'
        update_db = conn.execute(add_query, (name,))
        return update_db.lastrowid

def build_apply_url(referenznummer: str) -> str:
    # Public BA Jobsuche job detail page - constructed from the reference
    # number, same identifier used to hit the (undocumented) jobdetails API.
    return f"https://www.arbeitsagentur.de/jobsuche/jobdetail/{quote(referenznummer, safe='')}"

# Insert 1 posting into postings
def posting_loader(conn, data):
    try:
        firma = data.get('firma') or 'Unknown'
        referenznummer = data['referenznummer']
        stellenlokationen = data.get('stellenlokationen') or []
        location = stellenlokationen[0]['adresse'].get('ort') if stellenlokationen else None

        company_id = get_or_insert_company(conn, firma)
        query = 'INSERT INTO postings (company_id, referenznummer, \
                                        title, location, entfernung, publish_date, \
                                        start_date, contract_type, raw_description_text,\
                                        german_level_requirement, salary, apply_url) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)'

        values = (company_id, referenznummer, data.get('stellenangebotsTitel'), location,
                  data.get('entfernung'), data.get('datumErsteVeroeffentlichung'),
                  data.get('eintrittszeitraum', {}).get('von'),
                  data.get('stellenangebotsart'), None, None, None,
                  build_apply_url(referenznummer)
        )
        conn.execute(query, values)
    except sqlite3.IntegrityError:
        # Already loaded (same source + referenznummer) - expected on reruns.
        pass
    except (KeyError, IndexError, TypeError) as e:
        # One malformed posting (missing referenznummer, no location entries,
        # unexpected shape) shouldn't take down the whole load run.
        print(f"Skipping malformed posting ({data.get('referenznummer', '?')}): {e}")

# Orchestration
def run_load(conn):
    for file_path in Path("data/raw").glob("*.json"):
        with open(file_path, encoding='utf-8' ) as f:
            full_json = json.load(f)
            postings = full_json.get('ergebnisliste', [])
            for posting in postings:
                posting_loader(conn, posting)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    conn = db_connect.get_connection()
    run_load(conn)
