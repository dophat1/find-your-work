import sys 
import subprocess

result = subprocess.run([sys.executable, "src/ingest_ba.py"])
# result.returncode == 0 means success, anything else means the script errored

STEPS = [
    ("Ingest job postings from BA", "src/ingest_ba.py"),
    ("Load postings into database", "src/load_data.py"),
    ("Fetch full job descriptions", "src/fetch_jobs_details.py"),
    ("Extract skills", "src/extract_jobs_skills.py"),
    ("Extract German level requirements", "src/extract_jobs_ger_req.py"),
]