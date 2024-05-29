import json
import collections

with open('Data\DB\skill_db_processed.json', 'r+') as f:
    skills_db = json.load(f)

def get_dist_new(array):
    words = []
    for val in array:
        vals = val.split(' ')
        for v in vals:

            words.append(v)

    a = words
    counter = collections.Counter(a)
    counter = dict(counter)
    return counter


n_grams = [skills_db[key]['skill_cleaned'] for key in skills_db if skills_db[key]['skill_len'] > 1]
n_gram_dist = get_dist_new(n_grams)
# save
with open('Data\DB\Token_frequency.json', 'w', encoding='utf-8') as f:
    json.dump(n_gram_dist, f, ensure_ascii=False, indent=4)
