CREATE TABLE companies (
    company_id INTEGER PRIMARY KEY ,
    name varchar(255) NOT NULL UNIQUE,
    career_page_url varchar(255)
);

CREATE TABLE postings (
    posting_id INTEGER PRIMARY KEY, 
    company_id INTEGER REFERENCES companies(company_id),
    source varchar(255) DEFAULT 'BA',
    referenznummer varchar(255),
    title varchar(255),
    location varchar(255),
    entfernung INTEGER,
    publish_date date,
    contract_type varchar(255),
    raw_description_text text,
    extracted_skills varchar(255), 
    german_level_requirement varchar(255), 
    salary INTEGER, 
    UNIQUE(source, referenznummer)
);