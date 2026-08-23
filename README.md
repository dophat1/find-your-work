# Find Your Work

A small end-to-end pipeline that pulls German data/ML job postings from the Bundesagentur für Arbeit (BA) Jobsuche API, extracts structured requirements from the raw text, matches postings against a CV, and visualizes the results in a Streamlit dashboard.

## Pipeline

1. **`src/ingest_ba.py`** — queries the BA Jobsuche search API for a set of (city, keyword) combinations and saves the raw JSON responses to `data/raw/`. This hits an undocumented API reverse-engineered from the BA Jobsuche mobile app (see the commented-out iOS User-Agent in the file) — there's no public developer API for this.
2. **`src/load_data.py`** — reads the raw JSON dumps, upserts companies, and inserts postings into SQLite. Deduplicated via a `UNIQUE(source, referenznummer)` constraint, so re-running ingestion never creates duplicate rows.
3. **`src/fetch_jobs_details.py`** — for postings still missing a full description, calls a second BA endpoint (`jobdetails`) to fetch the raw text. The reference number has to be base64-encoded to build the URL — another undocumented detail found by inspecting the mobile app's traffic, not from any docs.
4. **`src/extract_jobs_skills.py`** — regex/dictionary keyword extraction of ~50 tech/data skills from the posting text into a `postings_skills` join table.
5. **`src/extract_jobs_ger_req.py`** — extracts the required German-language level (CEFR level or descriptive adjective) by scanning a token window around the word "deutsch" and prioritizing CEFR levels (B2/C1/C2) over adjectives when both appear in the window. `explore_data()` is the exploratory pass used to find the most frequent words that actually co-occur with "deutsch" before the extraction rule was designed.
6. **`src/match.py`** — extracts skills from a candidate's CV text and ranks postings by Jaccard similarity (intersection over union) against each posting's extracted skills. This is explicitly a **baseline** — see Limitations.
7. **`src/dashboard.py`** — Streamlit dashboard: contract-type breakdown, location breakdown, a distance-from-search-center histogram, and the top companies by posting count.

## Data model

`db/schema.sql` — three tables: `companies`, `postings` (FK to `companies`, unique on `(source, referenznummer)` to prevent duplicate ingestion), `postings_skills` (join table, unique on `(posting_id, skill_name)`).

## Tech stack

Python, `requests`, SQLite, regex-based extraction, pandas/numpy, Streamlit.

## Running it

```bash
git clone https://github.com/dophat1/find-your-work.git
cd find-your-work

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

Then run the pipeline:

```bash
python run_pipeline.py           # ingest -> load -> fetch details -> extract skills -> extract German level

python src/match.py              # rank postings against a CV
streamlit run src/dashboard.py   # explore the market
```

## Limitations / next steps

- Skill and German-level extraction are keyword/regex-based, not a trained model — they'll miss synonyms and phrasings the dictionary doesn't cover.
- The CV-posting matcher uses Jaccard similarity as a baseline. An obvious upgrade: TF-IDF or embedding-based similarity instead of raw set overlap.
- Depends on an undocumented, reverse-engineered API that could change without notice.
