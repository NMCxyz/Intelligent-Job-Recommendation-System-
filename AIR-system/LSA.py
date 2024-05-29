from typing import Optional, Dict, Union, List, Any
import string
import collections
import logging
import json
import os

import numpy as np

import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction import text 
from sklearn import decomposition

import GeneralParameter

nltk.download('stopwords')
nltk.download('wordnet')
stop_words = set(stopwords.words("english"))

logger = logging.getLogger()

def is_ascii(s: str) -> bool:
    return all(ord(c) < 128 for c in s)

def contains_digit(text: str) -> bool:
    return any(x.isdigit() for x in text)

def make_vocab(texts: str, num_vocab: Optional[int] = None,
                min_word_count: Optional[int] = None) -> None:
    if os.path.isfile(GeneralParameter.VOCAB_PATH):
        with open(GeneralParameter.VOCAB_PATH, 'r') as f:
            vocab = json.load(f)
        return vocab

    if num_vocab is None and min_word_count is None:
        raise ValueError('Either num_vocab or min_word_count must be provided')

    texts = texts.lower()
    texts = texts.translate(str.maketrans('', '', string.punctuation))
    
    texts = texts.split()
    texts = [x for x in texts if x not in stop_words and x not in string.punctuation and is_ascii(x) and not contains_digit(x)]
    lemma = nltk.wordnet.WordNetLemmatizer()
    texts = [lemma.lemmatize(x) for x in texts]

    counter = collections.Counter(texts)

    selected_words = []
    if min_word_count is None and num_vocab is not None:
        selected_words = counter.most_common(num_vocab)
        selected_words = [x[0] for x in selected_words if not x[0].isdigit()]
    elif min_word_count is not None:
        word_count = counter.most_common(len(texts))
        selected_words = [x[0] for x in word_count if x[1] >= min_word_count and not x[0].isdigit() ]

    vocab = {w: i+1 for i, w in enumerate(selected_words)}
    vocab['_unknown_'] = 0
    
    with open(GeneralParameter.VOCAB_PATH, 'w') as f:
        json.dump(vocab, f)

    return vocab

class LSA:

    def __init__(self, vocab: Dict[str, int], documents: List[str],
                num_features: Union[int, float]) -> None:
        self.vocab = vocab
        self.documents = documents
        self.num_features = num_features if num_features > 1 else int(num_features*len(self.vocab))
        
        self.lemmatizer = nltk.wordnet.WordNetLemmatizer()

        self.vectorizer = text.TfidfVectorizer(decode_error='replace', 
                            vocabulary=self.vocab, )
        self.svd = decomposition.TruncatedSVD(n_components=self.num_features,
                            random_state = 42)

    def preprocess_text(self, text: str) -> str:
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = text.split()
        text = [x for x in text if x not in stop_words and x not in string.punctuation and is_ascii(x) and not contains_digit(x)]
        text = [self.lemmatizer.lemmatize(x) for x in text]
        text = [x if x in self.vocab.keys() else '_unknown_' for x in text ]
        return ' '.join(text)

    def vectorize(self, document: str) -> np.ndarray:
        document = self.preprocess_text(document)
        tfidf = self.vectorizer.transform([document],)
        reduced_features = self.svd.transform(tfidf)
        return reduced_features

    def do_work(self) -> None:
        self.processed_documents = [self.preprocess_text(x) for x in self.documents]
        features_matrix = self.vectorizer.fit_transform(self.processed_documents)
        self.svd.fit(features_matrix)

if __name__ == '__main__':
    texts = 'system'
    print('\n\n--------------------------------')
    print(make_vocab(texts, min_word_count = 2))
