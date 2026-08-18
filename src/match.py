# Baseline model with jaccard scores

def calc_jaccard_score(cv_skills:set, postings_skills:set):
    union = len(cv_skills | postings_skills)
    inter = len(cv_skills & postings_skills)
    if union != 0:   
        jaccard_score = inter/union
        return jaccard_score
    else: 
        return 0
