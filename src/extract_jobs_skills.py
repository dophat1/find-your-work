import re 
import db_connect
import sqlite3

SKILLS_DICTIONARY = {
    'machine_learning':['machine learning', 'maschinelles lernen'],
    'python':['python'],
    'powerbi':['power bi', 'powerbi'],
    'statistics':['statistics', 'statistik', 'statistikmodell'],
    'scikit_learn':['scikit-learn'],
    'sql': ['sql'],
    'docker':['docker'],
    'aws': ['aws', 'amazon web services'],
    'azure': ['azure', 'microsoft azure'],
    'gcp': ['gcp', 'google cloud platform'],
    'spark': ['spark', 'apache spark'],
    'hadoop': ['hadoop', 'apache hadoop'],
    'airflow': ['airflow', 'apache airflow'],
    'kafka': ['kafka', 'apache kafka'],
    'snowflake': ['snowflake'],
    'databricks': ['databricks'],
    'tableau': ['tableau'],
    'excel': ['excel', 'microsoft excel'],
    'sap': ['sap'],
    'java': ['java'],
    'git': ['git'],
    'github': ['github'],
    'gitlab': ['gitlab'],
    'jira': ['jira'],
    'confluence': ['confluence'],
    'agile': ['agile'],
    'scrum': ['scrum'],
    'linux': ['linux'],
    'bash': ['bash'],
    'api': ['api', 'apis'],
    'tensorflow': ['tensorflow'],
    'pytorch': ['pytorch'],
    'pandas': ['pandas'],
    'numpy': ['numpy'],
    'keras': ['keras'],
    'javascript': ['javascript'],
    'powerpoint': ['powerpoint'],
    'visualisation': ['visualisierung', 'visualisation', 'visualization'],
    'nosql': ['nosql'],
    'html': ['html'],
    'erp': ['erp'],
    'word': ['word'],
    'matlab': ['matlab'],
    'dashboard': ['dashboard'],
    'postgresql': ['postgresql', 'postgres'],
    'oracle': ['oracle'],
    'cpp': ['c++'],
    'dotnet': ['.net'],
    'nodejs': ['node.js'],
    'spss': ['spss'],
    'css': ['css'],
    'mongodb': ['mongodb'],
    'redis': ['redis'],
    'kubernetes':['kubernetes', 'k8s']
}

def extract_skills(text, vocabulary):
    skills = set(())
    for skill in vocabulary.keys():
        for variant in vocabulary[skill]:
            founded = re.search(rf"(?<!\w){re.escape(variant)}(?!\w)", text, re.IGNORECASE)
            if founded:
                skills.add(skill)
    return skills

def update_skills_db():
    conn = db_connect.get_connection()
    get_job_descr_query = 'SELECT posting_id, raw_description_text FROM postings WHERE raw_description_text IS NOT NULL;'
    job_details = conn.execute(get_job_descr_query).fetchall()
    for job_detail in job_details:
        skills = extract_skills(job_detail[1], SKILLS_DICTIONARY)
        for skill in skills:
            try:   
                insert_query = 'INSERT INTO postings_skills (posting_id, skill_name) VALUES (?, ?)'
                values = (job_detail[0], skill)
                conn.execute(insert_query, values)
            except sqlite3.IntegrityError:
                pass
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_skills_db()
            