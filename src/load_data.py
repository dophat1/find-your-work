import sqlite3
import db_connect
from pathlib import Path
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

# Insert 1 posting into postings
def posting_loader(conn, data):
    try:
        company_id = get_or_insert_company(conn, data['firma'])
        query = 'INSERT INTO postings (company_id, referenznummer, \
                                        title, location, entfernung, publish_date, \
                                        start_date, contract_type, raw_description_text,\
                                        german_level_requirement, salary) VALUES (?,?,?,?,?,?,?,?,?,?,?)'
        
        values = (company_id, data['referenznummer'], data['stellenangebotsTitel'], data['stellenlokationen'][0]['adresse']['ort'], 
                  data['entfernung'], data['datumErsteVeroeffentlichung'], data['eintrittszeitraum']['von'], 
                  data['stellenangebotsart'], None, None, None
        )
        conn.execute(query, values)
    except sqlite3.IntegrityError:
        pass 

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