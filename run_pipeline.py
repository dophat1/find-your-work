import sys 
import subprocess

STEPS = [
    ("Ingest job postings from BA", "src/ingest_ba.py"),
    ("Load postings into database", "src/load_data.py"),
    ("Fetch full job descriptions", "src/fetch_jobs_details.py"),
    ("Extract skills", "src/extract_jobs_skills.py"),
    ("Extract German level requirements", "src/extract_jobs_ger_req.py"),
]

for label, step in STEPS:
    try:
        print(f"==={label}===")
        result = subprocess.run([sys.executable, step], check=True)
        print("Successfully extracted infos.")
    except subprocess.CalledProcessError as e: 
        print(f"There is {e} at {label}")
        sys.exit(1)