from spacy import displacy
from Skills_Detection.Word_Class import Text,Matchers, SkillsGetter
from Skills_Detection.Detection_Method import Method


def transform_json(data):
    transformed = {}
    for detection in ['full_matches', 'ngram_scored']:
        for item in data['results'][detection]:
            category = item['skill_category']
            subcategory = item['skill_subcategory']
            skill_name = item['skill_name']
            if category not in transformed:
                transformed[category] = {
                    "Skills Distribution": {},
                    "List Skills": [],
                    "Subcategories": {}
                }
            if skill_name not in transformed[category]["List Skills"]:
                transformed[category]["List Skills"].append(skill_name)
            if subcategory not in transformed[category]["Subcategories"]:
                transformed[category]["Subcategories"][subcategory] = []
                transformed[category]["Skills Distribution"][subcategory] = 0
            transformed[category]["Skills Distribution"][subcategory] += 1
            skill_details = {
                "skill_name": skill_name,
                "detection": detection,
                "score": item['score'],
                "doc_node_value": item['doc_node_value'],
                "skill_id": item['skill_id']
            }
            if detection == 'ngram_scored':
                skill_details['type'] = item.get('type')
                skill_details['len'] = item.get('len')
            transformed[category]["Subcategories"][subcategory].append(skill_details)
    return transformed

def filter_it_skills_and_update(annotations, fields):
    annotations["results"]["full_matches"] = [
        item for item in annotations["results"]["full_matches"]
        if item.get("skill_category") == fields
    ]
    annotations["results"]["ngram_scored"] = [
        item for item in annotations["results"]["ngram_scored"]
        if item.get("skill_category") == fields
    ]
    return annotations

class SkillExtractor:

    def __init__(
        self,
        nlp,
        skills_db,
        phraseMatcher,
        tranlsator_func=False
    ):
        self.tranlsator_func = tranlsator_func
        self.nlp = nlp
        self.skills_db = skills_db
        self.phraseMatcher = phraseMatcher
        self.matchers = Matchers(self.nlp, self.skills_db, self.phraseMatcher).load_matchers()
        self.skill_getters = SkillsGetter(self.nlp)
        self.utils = Method(self.nlp, self.skills_db)

    # def get_skill_info(self, skill_id):
    #     return self.skills_db.get(skill_id, {})

    
    def annotate(
        self,
        text: str,
        thresh: float = 0.5
    ) -> dict:
        if self.tranlsator_func:
            text = self.tranlsator_func(text)
        text_obj = Text(text, self.nlp)
        skills_full, text_obj = self.skill_getters.get_full_match_skills(text_obj, self.matchers['full_matcher'])
        skills_abv, text_obj = self.skill_getters.get_abv_match_skills(text_obj, self.matchers['abv_matcher'])
        skills_uni_full, text_obj = self.skill_getters.get_full_uni_match_skills(text_obj, self.matchers['full_uni_matcher'])
        skills_low_form, text_obj = self.skill_getters.get_low_match_skills(text_obj, self.matchers['low_form_matcher'])
        skills_on_token = self.skill_getters.get_token_match_skills(text_obj, self.matchers['token_matcher'])
        full_sk = skills_full + skills_abv
        to_process = skills_on_token + skills_low_form + skills_uni_full
        process_n_gram = self.utils.process_n_gram(to_process, text_obj)

        full_matches = []
        for full_match in full_sk:
            skill_info = self.skills_db.get(full_match["skill_id"])
            full_matches.append({
                "skill_id": full_match["skill_id"],
                "doc_node_value": full_match["doc_node_value"],
                "score": full_match["score"],
                "doc_node_id": full_match["doc_node_id"],
                "skill_category": skill_info.get("skill_category", ""),
                "skill_subcategory": skill_info.get("skill_subcategory", ""),
                "skill_name": skill_info.get("skill_name", "")
            })

        ngram_scored = []
        for ngram_match in process_n_gram:
            if ngram_match["score"] >= thresh:
                skill_info = self.skills_db.get(ngram_match["skill_id"])
                ngram_scored.append({
                    "skill_id": ngram_match["skill_id"],
                    "doc_node_value": ngram_match["doc_node_value"],
                    "score": ngram_match["score"],
                    "doc_node_id": ngram_match["doc_node_id"],
                    "type": ngram_match["type"],
                    "len": ngram_match["len"],
                    "skill_category": skill_info.get("skill_category", ""),
                    "skill_subcategory": skill_info.get("skill_subcategory", ""),
                    "skill_name": skill_info.get("skill_name", "")
                })

        return_data =  {
            'text': text_obj.transformed_text,
            'results': {
                'full_matches': full_matches,
                'ngram_scored': ngram_scored,
            }
        }
        data_to_transform = filter_it_skills_and_update(return_data, self.fields)
        return transform_json(data_to_transform)
        
        


