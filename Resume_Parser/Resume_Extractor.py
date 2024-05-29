from unidecode import unidecode
import fitz  # PyMuPDF
import pandas as pd
import json
import en_core_web_lg
import numpy as np
from spacy.matcher import PhraseMatcher

from Skills_Detection.Skill_Extractor import SkillExtractor
from Skills_Detection.GeneralParameter import SKILL_DB

class PDFSkillsExtractor:
    def __init__(self, my_path, fields="All"):
        self.my_path = my_path
        self.fields = fields

    def extract_skills_from_pdf(self):
        doc = fitz.open(self.my_path)
        text = ""
        for page in doc:
            text_page = page.get_text()
            text += text_page

        nlp = en_core_web_lg.load()

        skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher, self.fields)

        annotations = skill_extractor.annotate(text)

        def convert(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

        return json.dumps(annotations, default=convert)

if __name__ == "__main__":
    my_path = "Data\\InputPDF\\front-end-developer-resume-example.pdf"
    pdf_skills_extractor = PDFSkillsExtractor(my_path, "All")
    json_data = pdf_skills_extractor.extract_skills_from_pdf()
    print(json_data)
