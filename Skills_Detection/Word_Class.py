from typing import List
from Skills_Detection.Text_Cleaner import Cleaner, stem_text, find_index_phrase
from Skills_Detection.GeneralParameter import S_GRAM_REDUNDANT

import spacy

class Word:

    def __init__(
        self,
        word: str
    ) -> None:
        self.word = word
        self.lemmed = ""
        self.stemmed = ""
        self.is_stop_word = None
        self.is_matchable = True
        self.start: int
        self.end: int

    def metadata(self) -> dict:
        return {
            "lemmed": self.lemmed,
            "stemmed": self.stemmed,
            "is_stop_word": self.is_stop_word,
            "is_matachable": self.is_matchable
        }

    def __str__(self) -> str:
        return self.word

    def __len__(self) -> int:
        return len(self.word)

class Text:

    def __init__(
        self,
        text: str,
        nlp
    ):
        self.immutable_text = text
        cleaner = Cleaner(
            include_cleaning_functions=[
                "remove_punctuation",
                "remove_extra_space"
            ],
            to_lowercase=False
        )
        self.transformed_text = cleaner(text).lower()
        self.abv_text = cleaner(text)
        self.list_words = []
        doc = nlp(self.transformed_text)

        for token in doc:
            word = Word(token.text)
            word.lemmed = token.lemma_
            word.stemmed = stem_text(token.text)
            word.is_stop_word = token.is_stop
            if token.is_stop:
                word.is_matchable = False
            self.list_words.append(word)

        for redundant_word in S_GRAM_REDUNDANT:
            list_index = find_index_phrase(
                phrase=redundant_word, text=self.transformed_text)
            for index in list_index:
                self[index].is_matchable = False

    def stemmed(
        self,
        as_list: bool = False
    ):
        list_stems = [word.stemmed for word in self.list_words]
        if as_list:
            return list_stems
        return " ".join(list_stems)

    def lemmed(
        self,
        as_list: bool = False
    ):
        list_lems = [word.lemmed for word in self.list_words]
        if as_list:
            return list_lems
        return " ".join(list_lems)

    def __str__(self) -> str:
        return self.immutable_text

    def __getitem__(
        self,
        index: int
    ) -> Word:
        return self.list_words[index]

    def __len__(self) -> int:
        return len(self.list_words)

    @staticmethod
    def words_start_end_position(text: str) -> List[Word]:
        list_words = []
        pointer = 0
        for raw_word in text.split(" "):
            word = Word(raw_word)
            word.start = pointer
            word.end = pointer + len(word)
            pointer += len(word) + 1
            list_words.append(word)
        return list_words

    
class Matchers:
    # Initializes Matchers object with NLP model, skills database, and a phrase matcher.
    def __init__(self, nlp, skills_db, phraseMatcher):
        self.nlp = nlp
        self.skills_db = skills_db
        self.phraseMatcher = phraseMatcher
        self.dict_matcher = {
            'full_matcher': self.get_full_matcher,
            'abv_matcher': self.get_abv_matcher,
            'full_uni_matcher': self.get_full_uni_matcher,
            'low_form_matcher': self.get_low_form_matcher,
            'token_matcher': self.get_token_matcher,
        }

    def load_matchers(self, include=['full_matcher', 'abv_matcher', 'full_uni_matcher', 'low_form_matcher', 'token_matcher'], exclude=[]):
        loaded_matchers = {}
        if len(exclude):
            for matcher_name, matcher in self.dict_matcher.items():
                if matcher_name not in exclude:
                    print(f"loading {matcher_name} ...")
                    loaded_matchers[matcher_name] = matcher()
        else:
            for matcher_name, matcher in self.dict_matcher.items():
                if matcher_name in include:
                    print(f"loading {matcher_name} ...")
                    loaded_matchers[matcher_name] = matcher()
        return loaded_matchers

    # Initializes and returns a matcher for full skill names.
    def get_full_matcher(self):
        nlp = self.nlp
        skills_db = self.skills_db
        full_matcher = self.phraseMatcher(nlp.vocab, attr="LOWER")
        for key in skills_db:
            skill_id = key
            skill_len = skills_db[key]['skill_len']
            if skill_len > 1:
                skill_full_name = skills_db[key]['high_surfce_forms']['full']
                skill_full_name_spacy = nlp.make_doc(skill_full_name)
                full_matcher.add(str(skill_id), [skill_full_name_spacy])
        return full_matcher
    
    # Extracts skills based on abbreviations in the text.
    def get_abv_matcher(self):
        nlp = self.nlp
        skills_db = self.skills_db
        abv_matcher = self.phraseMatcher(nlp.vocab, attr="LOWER")
        for key in skills_db:
            skill_id = key
            if 'abv' in skills_db[key]['high_surfce_forms'].keys():
                skill_abv = skills_db[key]['high_surfce_forms']['abv']
                skill_abv_spacy = nlp.make_doc(skill_abv)
                abv_matcher.add(str(skill_id), [skill_abv_spacy])
        return abv_matcher

    # Initializes and returns a matcher for single-word full skill names.
    def get_full_uni_matcher(self):
        nlp = self.nlp
        skills_db = self.skills_db
        full_uni_matcher = self.phraseMatcher(nlp.vocab, attr="LOWER")
        for key in skills_db:
            skill_id = key
            skill_len = skills_db[key]['skill_len']
            if skill_len == 1:
                skill_full_name = skills_db[key]['high_surfce_forms']['full']
                skill_full_name_spacy = nlp.make_doc(skill_full_name)
                full_uni_matcher.add(str(skill_id), [skill_full_name_spacy])
        return full_uni_matcher

    # Initializes and returns a matcher for low surface forms of skills.
    def get_low_form_matcher(self):
        nlp = self.nlp
        skills_db = self.skills_db
        low_form_matcher = self.phraseMatcher(nlp.vocab, attr="LOWER")
        for key in skills_db:
            skill_id = key
            skill_len = skills_db[key]['skill_len']
            low_surface_forms = skills_db[key]['low_surface_forms']
            for form in low_surface_forms:
                skill_form_spacy = nlp.make_doc(form)
                low_form_matcher.add(str(skill_id), [skill_form_spacy])
        return low_form_matcher

    # Initializes and returns a matcher for individual tokens.
    def get_token_matcher(self):
        nlp = self.nlp
        skills_db = self.skills_db
        token_matcher = self.phraseMatcher(nlp.vocab, attr="LOWER")
        for key in skills_db:
            skill_id = key
            match_on_tokens = skills_db[key]['match_on_tokens']
            if match_on_tokens:
                skill_lemmed = skills_db[key]['high_surfce_forms']['full']
                skill_lemmed_tokens = skill_lemmed.split(' ')
                for token in skill_lemmed_tokens:
                    if not token.isdigit():
                        id = skill_id
                        token_matcher.add(str(id), [nlp.make_doc(token)])
        return token_matcher


class SkillsGetter:
    def __init__(self, nlp):
        self.nlp = nlp

    # Extracts skills based on full matches in the text.
    def get_full_match_skills(self, text_obj, matcher):
        skills = []
        doc = self.nlp(text_obj.lemmed())
        for match_id, start, end in matcher(doc):
            id = matcher.vocab.strings[match_id]
            skills.append({'skill_id': id, 'doc_node_value': str(doc[start:end]), 'score': 1, 'doc_node_id': list(range(start, end))})
            for token in text_obj[start:end]:
                token.is_matchable = False
        return skills, text_obj

    # Extracts skills based on abbreviations in the text.
    def get_abv_match_skills(self, text_obj, matcher):
        skills = []
        doc = self.nlp(text_obj.abv_text)
        for match_id, start, end in matcher(doc):
            id = matcher.vocab.strings[match_id]
            if text_obj[start].is_matchable:
                skills.append({'skill_id': id, 'score': 1, 'doc_node_value': str(doc[start:end]), 'doc_node_id': [start]})
                for token in text_obj[start:end]:
                    token.is_matchable = False
        return skills, text_obj

    # Extracts skills based on single-word full matches.
    def get_full_uni_match_skills(self, text_obj, matcher):
        skills = []
        doc = self.nlp(text_obj.transformed_text)
        for match_id, start, end in matcher(doc):
            id = matcher.vocab.strings[match_id]
            if text_obj[start].is_matchable:
                skills.append({'skill_id': id+'_fullUni', 'score': 1, 'doc_node_value': str(doc[start:end]), 'doc_node_id': [start], 'type': 'full_uni'})
        return skills, text_obj

    # Extracts skills based on individual token matches.
    def get_token_match_skills(self, text_obj, matcher):
        skills = []
        doc = self.nlp(text_obj.lemmed())
        for match_id, start, end in matcher(doc):
            id = matcher.vocab.strings[match_id]
            if text_obj[start].is_matchable:
                skills.append({'skill_id': id+'_oneToken', 'doc_node_value': str(doc[start:end]), 'doc_node_id': [start], 'type': 'one_token'})
        return skills

    # Extracts skills based on low surface form matches.
    def get_low_match_skills(self, text_obj, matcher):
        skills = []
        doc = self.nlp(text_obj.stemmed())
        for match_id, start, end in matcher(doc):
            id = matcher.vocab.strings[match_id]
            start = start if start < len(text_obj) else start - 1
            if text_obj[start].is_matchable:
                skills.append({'skill_id': id+'_lowSurf', 'doc_node_value': str(doc[start:end]), 'doc_node_id': list(range(start, end)), 'type': 'lw_surf'})
        return skills, text_obj

def main():
    nlp = spacy.load("en_core_web_lg")
    sample_text = "experimental in both English and French is mandatory."
    text_obj = Text(sample_text, nlp)
    first_word = text_obj[6]
    print("\nTừ đầu tiên và metadata của nó:")
    print(f"Từ: {first_word}")
    print("Metadata:", first_word.metadata())
if __name__ == "__main__":
    main()