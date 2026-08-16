import re
import db_connect

conn = db_connect.get_connection()
query = 'SELECT raw_description_text FROM postings WHERE raw_description_text IS NOT NULL'
result = conn.execute(query).fetchall()
texts = [row[0] for row in result]
match = []
count = 0
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

print(sorted(freq_dict.items(), key=lambda item: item[1],reverse=True))

