import sqlite3

def get_connection(db_path="db/jobs.db"):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn