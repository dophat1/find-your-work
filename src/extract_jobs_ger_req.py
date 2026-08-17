import re
import db_connect


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
    tokens = re.findall(r'\w+', text.lower(), re.IGNORECASE)
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
                    # Find all german proficiency level in the text
                        founded = []
                        for word in words_around_ger_prof:
                            if word in ['b2', 'c1', 'c2']:
                                founded.append(word)
                            else:
                                founded.append(ger_prof)
                        
                        # Scanning and extracting the german proficiency, rules: CEFR > adjective
                        cefr_level = [level for level in founded if level in ['b2', 'c1', 'c2']]
                        if cefr_level:
                            ger_prof = cefr_level[0]
                        elif founded:
                            ger_prof = founded[0]
                        else: 
                            ger_prof = None
    
    return ger_prof

