import json
from Skills_Detection.Text_Cleaner import remove_punctuation, stem_text, lem_text, PorterStemmer
import spacy

nlp = spacy.load("en_core_web_lg")

def process_skills(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)['data']

    processed_skills = {}

    for skill in data:
        skill_id = skill['id']
        skill_name = skill['name']
        skill_type = skill.get('type', {}).get('name', '')
        skill_category = skill.get('category', {}).get('name', '')
        skill_subcategory = skill.get('subcategory', {}).get('name', '')
        skill_cleaned = remove_punctuation(skill_name).lower()
        skill_stemmed = stem_text(skill_cleaned)
        skill_lemmed = lem_text(skill_cleaned, nlp)
        skill_len = len(skill_cleaned.split(' '))
        match_on_stemmed = skill_len == 1
        abbreviation = ''  # Extract this from your database if available

        processed_skills[skill_id] = {
            "skill_name": skill_name,
            "skill_cleaned": skill_cleaned,
            "skill_type": skill_type,
            "skill_category": skill_category,
            "skill_subcategory": skill_subcategory,
            "skill_lemmed": skill_lemmed,
            "skill_stemmed": skill_stemmed,
            "skill_len": skill_len,
            "abbreviation": abbreviation,
            "match_on_stemmed": match_on_stemmed
        }
    with open('Data\DB\skill_db_processed.json', 'w') as outfile:
        json.dump(processed_skills, outfile, indent=4)
process_skills('Data\DB\skill_db_24_newest.json')
