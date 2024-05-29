# installed packs
from nltk.stem import PorterStemmer
from typing import List
from Skills_Detection.GeneralParameter import S_GRAM_REDUNDANT, LIST_PUNCTUATIONS
import spacy

# remove punctuation from text
def remove_punctuation(text, list_punctuations=LIST_PUNCTUATIONS):
    for punc in list_punctuations:
        text = text.replace(punc, " ")
    return text.strip()

# remove redundant words
def remove_redundant(text, list_redundant_words=S_GRAM_REDUNDANT):
    for phrase in list_redundant_words:
        text = text.replace(phrase, "")
    return text.strip()

# stem using a predefined stemmer
def stem_text(text, stemmer=PorterStemmer()):
    return " ".join([stemmer.stem(word) for word in text.split(" ")])

# lem text using nlp loaded from spacy
def lem_text(text, nlp):
    doc = nlp(text)
    return ' '.join([token.lemma_ for token in doc])

# remove extra space
def remove_extra_space(text):
    return " ".join(text.split())

# gather all cleaning functions in a dict
dict_cleaning_functions = {
    "remove_punctuation": remove_punctuation,
    "remove_redundant": remove_redundant,
    "stem_text": stem_text,
    "lem_text": lem_text,
    "remove_extra_space": remove_extra_space
}

# find index of words of a phrase in a text
def find_index_phrase(phrase, text):
    if phrase in text:
        list_words = text.split(" ")
        list_phrase_words = phrase.split(" ")
        n = len(list_phrase_words)
        for i in range(len(text) - n):
            if list_words[i:i + n] == list_phrase_words:
                return [i + k for k in range(n)]
    return []

# A class to build pipelines to clean text
class Cleaner:
    def __init__(self, to_lowercase=True, include_cleaning_functions=dict_cleaning_functions, exclude_cleaning_function=[]):
        self.include_cleaning_functions = include_cleaning_functions
        self.exclude_cleaning_functions = exclude_cleaning_function
        self.to_lowercase = to_lowercase

    def __call__(self, text):
        if self.to_lowercase:
            text = text.lower()
        if len(self.exclude_cleaning_functions):
            for cleaning_name in dict_cleaning_functions.keys():
                if cleaning_name not in self.exclude_cleaning_functions:
                    if cleaning_name == "lem_text":
                        text = dict_cleaning_functions[cleaning_name](text, nlp)
                    else:
                        text = dict_cleaning_functions[cleaning_name](text)
        else:
            for cleaning_name in dict_cleaning_functions.keys():
                if cleaning_name in self.include_cleaning_functions:
                    if cleaning_name == "lem_text":
                        text = dict_cleaning_functions[cleaning_name](text, nlp)
                    else:
                        text = dict_cleaning_functions[cleaning_name](text)
        return text

if __name__ == '__main__':
    nlp = spacy.load("en_core_web_lg")
    sample_text = "This is a sample text, containing various elements like numbers 123, special characters %&!, and different types of punctuation."
    cleaner = Cleaner(
        to_lowercase=True,
        include_cleaning_functions=["remove_punctuation","remove_redundant", "remove_extra_space", "stem_text"]
    )
    cleaner_text = "This is another experimental text, with EXTRA spaces and PUNCTUATION!!!"
    print("\nUsing Cleaner class:")
    print("Original text:")
    print(cleaner_text)
    print("Cleaned text:")
    print(cleaner(cleaner_text))