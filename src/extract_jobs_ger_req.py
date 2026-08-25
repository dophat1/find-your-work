import re
import db_connect
import sqlite3


GERMAN_LEVEL_DICTIONARY = {
    'good':['gute', 'guten', 'gut', 'gutes'],
    'really_good':['sehr gut', 'sehr gute', 'sehr guten'],
    'fluent':['fließende', 'fließend', 'fließendes'],
    'business_fluent':['verhandlungssichere', 'verhandlungssicheres', 'verhandlungssicher'],
    'b2':['b2'],
    'c1':['c1'],
    'c2':['c2'],
    'grundkenntnisse':['grundkenntnisse']
}

# When multiple German-level mentions are found in the same posting, this is
# the order used to pick a single "best" one: CEFR levels win over adjective
# descriptions (a posting mentioning both "B2" and "gute Deutschkenntnisse"
# should report the more precise B2), and within adjectives, stronger phrasing
# wins over weaker phrasing.
GERMAN_LEVEL_PRIORITY = ['c2', 'c1', 'b2', 'business_fluent', 'fluent', 'really_good', 'good', 'grundkenntnisse']

# Find the list of most frequent words appear alongside the word 'deutsch'
def explore_data():
    conn = db_connect.get_connection()
    query = 'SELECT raw_description_text FROM postings WHERE raw_description_text IS NOT NULL'
    result = conn.execute(query).fetchall()
    texts = [row[0] for row in result]
    match = []
    freq_dict = {}

    for text in texts: 
        tokens = re.findall(r'\w+', text.lower(), re.IGNORECASE)
        for index, tokenized_text in enumerate(tokens):
            if 'deutsch' in tokenized_text:
                start = max(0, index - 4)
                end = index + 5
                word_around_german = tokens[start:end]
                match.append(word_around_german)

    for match_list in match:
        for word in match_list: 
            if word not in freq_dict:
                freq_dict.update({word:1})
            else:
                freq_dict[word] += 1

    return sorted(freq_dict.items(), key=lambda item: item[1],reverse=True)


def extract_ger_prof(text, vocabulary):
    """
    Scan the whole document for every (adjective/CEFR) mention that occurs
    near the word 'deutsch', collect all of them, then return a single best
    answer using GERMAN_LEVEL_PRIORITY.

    v1 of this function re-assigned ger_req on every vocabulary-key loop
    iteration, so whichever vocabulary key happened to be checked *last*
    silently overwrote a better, earlier match found elsewhere in the same
    posting (e.g. "grundkenntnisse" mentioned in an unrelated sentence could
    stomp a "C1" match found earlier). This version collects every valid
    match across the whole text first, then applies one consistent priority.
    """
    tokens = re.findall(r'\w+', text.lower(), re.IGNORECASE)
    found_levels = set()

    for ger_prof in vocabulary.keys():
        for variant in vocabulary[ger_prof]:
            for index, tokenized_text in enumerate(tokens):
                # Join to check for consecutive tokens like 'sehr gut'
                if variant in ' '.join(tokens[index:index+2]):
                    start = max(0, index - 4)
                    end = index + 5
                    words_around_ger_prof = tokens[start:end]
                    has_deutsch = any('deutsch' in word for word in words_around_ger_prof)
                    if has_deutsch:
                        # CEFR levels found in this window take priority over
                        # the adjective vocabulary key for this window.
                        cefr_in_window = [w for w in words_around_ger_prof if w in ('b2', 'c1', 'c2')]
                        found_levels.add(cefr_in_window[0] if cefr_in_window else ger_prof)

    for level in GERMAN_LEVEL_PRIORITY:
        if level in found_levels:
            return level
    return None

def update_ger_prof_req():
    conn = db_connect.get_connection()
    get_job_descr_query = 'SELECT posting_id, raw_description_text FROM postings WHERE raw_description_text IS NOT NULL;'
    job_details = conn.execute(get_job_descr_query).fetchall()
    for job_detail in job_details:
        ger_prof_req = extract_ger_prof(job_detail[1], GERMAN_LEVEL_DICTIONARY)
        try:
            update_query = 'UPDATE postings SET german_level_requirement = ? WHERE posting_id = ?'
            values = (ger_prof_req, job_detail[0])
            conn.execute(update_query, values)
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()

if __name__ =="__main__":
    update_ger_prof_req()
