import argparse
import csv
import sys
from pathlib import Path

from extract_jobs_skills import extract_skills, SKILLS_DICTIONARY
from db_connect import get_connection

# Baseline model with jaccard scores
def calc_jaccard_score(cv_skills: set, postings_skills: set):
    union = len(cv_skills | postings_skills)
    inter = len(cv_skills & postings_skills)
    if union != 0:
        return inter / union
    return 0


def matching(cv, vocabulary):
    conn = get_connection()
    # LEFT JOIN so postings with zero extracted skills still get a row
    # (skill_name will be NULL for those), instead of being dropped entirely.
    select_query = '''
        SELECT p.posting_id, ps.skill_name
        FROM postings p
        LEFT JOIN postings_skills ps ON p.posting_id = ps.posting_id
    '''
    select_results = conn.execute(select_query).fetchall()
    conn.close()

    cv_skills = extract_skills(cv, vocabulary)

    # Put the skills from the table to the form {'posting_id':{skill1, skill2, skill3,...}}
    posting_skills = {}
    for posting_id, skill_name in select_results:
        if posting_id not in posting_skills:
            posting_skills[posting_id] = set()
        # NULL skill_name means "no skills found for this posting" (from the
        # LEFT JOIN) -- don't let it get added as a literal skill in the set.
        if skill_name is not None:
            posting_skills[posting_id].add(skill_name)

    result = []
    for posting_id, posting_skills_set in posting_skills.items():
        jaccard_score = calc_jaccard_score(cv_skills, posting_skills_set)
        result.append((posting_id, jaccard_score))

    return sorted(result, key=lambda x: x[1], reverse=True), cv_skills


def get_posting_details(posting_ids):
    """Join posting_ids back to human-readable info: title, company, location,
    German level requirement, and the apply link. Returns {posting_id: dict}."""
    if not posting_ids:
        return {}
    conn = get_connection()
    placeholders = ",".join("?" * len(posting_ids))
    query = f'''
        SELECT p.posting_id, p.title, c.name, p.location, p.german_level_requirement,
               p.contract_type, p.apply_url
        FROM postings p
        JOIN companies c ON p.company_id = c.company_id
        WHERE p.posting_id IN ({placeholders})
    '''
    rows = conn.execute(query, posting_ids).fetchall()
    conn.close()
    details = {}
    for posting_id, title, company, location, german_level, contract_type, apply_url in rows:
        details[posting_id] = {
            "title": title,
            "company": company,
            "location": location,
            "german_level_requirement": german_level,
            "contract_type": contract_type,
            "apply_url": apply_url,
        }
    return details


def load_cv(cv_path: str) -> str:
    path = Path(cv_path)
    if not path.exists():
        raise FileNotFoundError(f"CV file not found: {cv_path}")
    if path.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            raise SystemExit(
                "Reading a .pdf CV needs pypdf. Install it with: pip install pypdf\n"
                "Or export your CV to a .txt file and pass that instead."
            )
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return path.read_text(encoding="utf-8", errors="ignore")


def print_results(ranked, details, cv_skills, top_n):
    print(f"\nExtracted {len(cv_skills)} skill(s) from your CV: {', '.join(sorted(cv_skills)) or '(none found)'}\n")
    shown = [r for r in ranked if r[1] > 0][:top_n] or ranked[:top_n]
    print(f"Top {len(shown)} matching postings:\n")
    for rank, (posting_id, score) in enumerate(shown, start=1):
        info = details.get(posting_id, {})
        print(f"{rank}. [{score:.0%} match] {info.get('title', '(unknown title)')}")
        print(f"   {info.get('company', '(unknown company)')} - {info.get('location', '?')} - {info.get('contract_type') or '?'}")
        if info.get("german_level_requirement"):
            print(f"   German level required: {info['german_level_requirement']}")
        print(f"   Apply: {info.get('apply_url', '(no link)')}")
        print()


def write_csv(ranked, details, out_path):
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["rank", "score", "title", "company", "location", "contract_type",
                          "german_level_requirement", "apply_url"])
        for rank, (posting_id, score) in enumerate(ranked, start=1):
            info = details.get(posting_id, {})
            writer.writerow([rank, f"{score:.4f}", info.get("title"), info.get("company"),
                              info.get("location"), info.get("contract_type"),
                              info.get("german_level_requirement"), info.get("apply_url")])
    print(f"Full ranked list written to {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Rank scraped job postings against your CV.")
    parser.add_argument("--cv", required=True, help="Path to your CV (.txt or .pdf)")
    parser.add_argument("--top", type=int, default=10, help="How many top matches to print (default 10)")
    parser.add_argument("--csv", help="Optional path to write the full ranked list as CSV")
    args = parser.parse_args()

    cv_text = load_cv(args.cv)
    ranked, cv_skills = matching(cv_text, SKILLS_DICTIONARY)

    if not ranked:
        print("No postings found in the database. Run run_pipeline.py first.")
        sys.exit(1)

    details = get_posting_details([pid for pid, _ in ranked])
    print_results(ranked, details, cv_skills, args.top)

    if args.csv:
        write_csv(ranked, details, args.csv)


if __name__ == "__main__":
    main()
