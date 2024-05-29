from Skills_Detection.GeneralParameter import TOKEN_DIST
from Skills_Detection.Word_Class import Text

import collections
import json
import functools
import math
import numpy as np
import jellyfish
import spacy
import pandas as pd
        
class Method:
    def __init__(self, nlp, skills_db):
        self.nlp = nlp
        self.skills_db = skills_db
        self.token_dist = TOKEN_DIST
        self.sign = functools.partial(math.copysign, 1)

    def make_one(self, cluster, len_):
        a = [1] * len_
        return [1*(i in cluster) for i, one in enumerate(a)]

    def split_at_values(self, lst, val):
        return [i for i, x in enumerate(lst) if x != val]

    def grouper(self, iterable, dist):
        prev = None
        group = []
        for item in iterable:
            if prev == None or item - prev <= dist:
                group.append(item)
            else:
                yield group
                group = [item]
            prev = item
        if group:
            yield group

    def get_clusters(self, co_oc):
        clusters = []
        for i, row in enumerate(co_oc):
            clusts = list(self.grouper(self.split_at_values(row, 0), 1))
            if clusts != []:
                a = [c for c in clusts if i in c][0]
                if a not in clusters:
                    clusters.append(a)
        return clusters

    def get_corpus(self, text, matches):
        len_ = len(text)
        corpus = []
        look_up = {}
        unique_skills = list(set([match['skill_id'] for match in matches]))
        skill_text_match_bin = [0]*len_
        for index, skill_id in enumerate(unique_skills):
            on_inds_ = [match['doc_node_id'] for match in matches if match['skill_id'] == skill_id]
            on_inds = [j for sub in on_inds_ for j in sub]
            skill_text_match_bin_updated = [(i in on_inds)*1 for i, _ in enumerate(skill_text_match_bin)]
            corpus.append(skill_text_match_bin_updated)
            look_up[index] = skill_id
        return np.array(corpus), look_up

    def one_gram_sim(self, text_str, skill_str):
        text = text_str + ' ' + skill_str
        tokens = self.nlp(text)
        token1, token2 = tokens[0], tokens[1]
        try:
            vec_similarity = token1.similarity(token2)
            return vec_similarity
        except:
            str_distance_similarity = jellyfish.jaro_distance(text_str.lower(), skill_str.lower())
            return str_distance_similarity

    def compute_w_ratio(self, skill_id, matched_tokens):
        skill_name = self.skills_db[skill_id]['high_surfce_forms']['full'].split(' ')
        skill_len = self.skills_db[skill_id]['skill_len']
        late_match_penalty_coef = 0.1
        token_ids = sum([(1-late_match_penalty_coef*skill_name.index(token)) for token in matched_tokens])
        return token_ids/skill_len

    def retain(self, text_obj, span, skill_id, sk_look, corpus):
        real_id, type_ = sk_look[skill_id].split('_')
        len_ = self.skills_db[real_id]['skill_len']
        len_condition = corpus[skill_id].dot(span)
        s_gr = np.array(list(span))*np.array(list(corpus[skill_id]))
        s_gr_n = [idx for idx, element in enumerate(s_gr) if element == 1]
        if type_ == 'oneToken':
            score = self.compute_w_ratio(real_id, [text_obj[ind].lemmed for ind in s_gr_n])
        if type_ == 'fullUni':
            score = 1
        if type_ == 'lowSurf':
            if len_ > 1:
                score = sum(s_gr)
            else:
                text_str = ' '.join([str(text_obj[i]) for i, val in enumerate(s_gr) if val == 1])
                skill_str = self.skills_db[real_id]['high_surfce_forms']['full']
                score = self.one_gram_sim(text_str, skill_str)
        return {'skill_id': real_id, 'doc_node_id':  [i for i, val in enumerate(s_gr) if val == 1], 'doc_node_value': ' '.join([str(text_obj[i]) for i, val in enumerate(s_gr) if val == 1]), 'type': type_, 'score': score, 'len': len_condition}

    def process_n_gram(self, matches, text_obj: Text):
        if len(matches) == 0:
            return matches
        text_tokens = text_obj.lemmed(as_list=True)
        len_ = len(text_tokens)
        corpus, look_up = self.get_corpus(text_tokens, matches)
        co_occ = np.matmul(corpus.T, corpus)
        clusters = self.get_clusters(co_occ)
        ones = [self.make_one(cluster, len_) for cluster in clusters]
        spans_conflicts = [(np.array(one), np.array([a_[0] for a_ in np.argwhere(corpus.dot(one) != 0)])) for one in ones]
        new_spans = []
        for span_conflict in spans_conflicts:
            span, skill_ids = span_conflict
            span_scored_skills = []
            types = []
            scores = []
            lens = []
            for sk_id in skill_ids:
                scored_sk_obj = self.retain(text_obj, span, sk_id, look_up, corpus)
                span_scored_skills.append(scored_sk_obj)
                types.append(scored_sk_obj['type'])
                lens.append(scored_sk_obj['len'])
                scores.append(scored_sk_obj['score'])
            if 'oneToken' in types and len(set(types)) > 1:
                id_ = np.array(scores).argmax()
                max_score = 0.5
                for i, len_ in enumerate(lens):
                    if len_ > 1 and types[i] == 'oneToken':
                        if scores[i] >= max_score:
                            id_ = i
                new_spans.append(span_scored_skills[id_])
            else:
                max_score_index = np.array(scores).argmax()
                new_spans.append(span_scored_skills[max_score_index])
        return new_spans

if __name__ == '__main__':
    nlp = spacy.load("en_core_web_lg")
    skills_db = {
        'skill1': {
            'skill_len': 2,
            'high_surfce_forms': {'full': 'Data Science'},
        },
        'skill2': {
            'skill_len': 3,
            'high_surfce_forms': {'full': 'Machine Learning'},
        }
    }
    utils = Method(nlp, skills_db)
    text = "This is a project involving data science and machine learning techniques."
    text_obj = Text(text, nlp)  
    matches = [
        {'skill_id': 'skill1', 'doc_node_id': [4, 5], 'type': 'fullUni'},
        {'skill_id': 'skill2', 'doc_node_id': [7, 8, 9], 'type': 'lowSurf'}
    ]
    processed_matches = utils.process_n_gram(matches, text_obj)
    print(processed_matches)