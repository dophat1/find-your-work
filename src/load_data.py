import sqlite3

def get_or_insert_company(conn, name):
    query = 'SELECT company_id FROM companies WHERE name = ?'
    result = conn.execute(query, (name,)).fetchone()
    if result is not None:
        return result[0]
    else: 
        add_query = 'INSERT INTO companies (name) VALUES (?)'
        update_db = conn.execute(add_query, (name,))
        return update_db.lastrowid
