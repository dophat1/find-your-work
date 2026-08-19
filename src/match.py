from extract_jobs_skills import extract_skills, SKILLS_DICTIONARY
from db_connect import get_connection

# Baseline model with jaccard scores
def calc_jaccard_score(cv_skills:set, postings_skills:set):
    union = len(cv_skills | postings_skills)
    inter = len(cv_skills & postings_skills)
    if union != 0:   
        jaccard_score = inter/union
        return jaccard_score
    else: 
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
        jaccard_score = calc_jaccard_score(cv_skills,posting_skills_set)
        result.append((posting_id, jaccard_score))
    
    return sorted(result, key=lambda x: x[1], reverse=True)