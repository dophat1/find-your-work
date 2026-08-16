import re 

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
}

def extract_skills(text, vocabulary):
    skills = set(())
    for skill in vocabulary.keys():
        for variant in vocabulary[skill]:
            founded = re.search(rf"\b{re.escape(variant)}\b", text, re.IGNORECASE)
            if founded:
                skills.add(skill)
            else:
                pass
    return skills