from typing import List
import re

import numpy as np
import pandas as pd
import networkx as nx
from scipy.spatial import distance

from LSA import *
import GeneralParameter

class JobRecommender:
    def __init__(self, G: nx.MultiDiGraph, lsa: LSA, ):
        self.G = G
        self.lsa = lsa
        self.all_node_types = ['candidate', 'employer', 'job']

        self.target_node = None

    def _add_employer_node(self, data: Dict[str, Any]) -> None:
        raise NotImplementedError()

    def _add_job_node(self, data: Dict[str, Any]) -> None:
        raise NotImplementedError()

    def _add_candidate_node(self, data: Dict[str, Any]) -> None:
        node_name = f"candidate-{self.G.graph['num_candidates']}"
        
        processed_resume = self.lsa.preprocess_text(data['resume'])
        vectorized_resume = self.lsa.vectorize(processed_resume)
        
        self.G.add_node(node_name, node_type = 'candidate', 
                        reduced_tfidf = vectorized_resume, **data)
        self.G.graph['num_candidates'] += 1

        self.target_node = node_name

        candidate_node_names = []
        job_node_names = []
        all_expertise = []

        for n in self.G: 
            this_node_type = self.G.nodes[n]['node_type']
            if this_node_type == 'job':
                job_node_names.append(n)
                continue
            if this_node_type == 'employer':
                continue
            elif this_node_type == 'candidate':
                candidate_node_names.append(n)
                
                this_node_expertise = self.G.nodes[n]['expertise']
                if this_node_expertise not in all_expertise:
                    all_expertise.append(this_node_expertise)

                if this_node_expertise == data['expertise']:
                    self.G.add_edge(node_name, n,
                                edge_type = 'expertise_match',
                                weight = GeneralParameter.EXPERTISE_MATCH_WEIGHT)
                    self.G.add_edge(n, node_name,
                                edge_type = 'expertise_match',
                                weight = GeneralParameter.EXPERTISE_MATCH_WEIGHT)

                    self.G.graph['expertise_match'] += 1

        self.all_expertise = all_expertise
        
        for name in candidate_node_names:
            this_node_vector = np.array(self.G.nodes[name]['reduced_tfidf']).flatten()
            vectorized_resume = vectorized_resume.flatten()
            sim = 1 - distance.cosine(vectorized_resume, this_node_vector)
            if sim > GeneralParameter.COSINE_SIMILARITY_THRESHOLD:
                self.G.add_edge(node_name, name,
                                edge_type='candidate_to_candidate',
                                weight=GeneralParameter.CANDIDATE_TO_CANDIDATE_WEIGHT,
                                cosine_similarity=sim)

                self.G.add_edge(name, node_name, 
                                edge_type='candidate_to_candidate',
                                weight=GeneralParameter.COSINE_SIMILARITY_THRESHOLD,
                                cosine_similarity=sim)

                self.G.graph['candidate_to_candidate'] += 1

        for name in job_node_names:
            this_node_vector = np.array(self.G.nodes[name]['reduced_tfidf']).flatten()
            vectorized_resume = vectorized_resume.flatten()
            sim = 1 - distance.cosine(vectorized_resume, this_node_vector)
            if sim > GeneralParameter.PROFILE_MATCHED_SIMILARITY_THRESDHOLD:
                self.G.add_edge(node_name, name, 
                                edge_type='candidate_to_job',
                                weight=GeneralParameter.CANDIDATE_TO_JOB_WEIGHT,
                                cosine_similarity=sim)

                self.G.add_edge(name, node_name, 
                                edge_type='candidate_to_job',
                                weight=GeneralParameter.CANDIDATE_TO_JOB_WEIGHT,
                                cosine_similarity=sim)

                self.G.graph['candidate_to_job'] += 1
    
    def add_node_to_graph(self, node_type: str,
                    node_data: Dict[str, Any]) -> None:
        
        if node_type not in self.all_node_types:
            raise ValueError(f'Node type must be one of {self.all_node_types}, received {node_type} instead.')

        if node_type == 'candidate':
            self._add_candidate_node(node_data)

        if node_type == 'employer':
            self._add_employer_node(node_data)

        if node_type == 'job':
            self._add_job_node(node_data)

    def rank_nodes(self,
                personalized: bool = False,
                target_node: Optional[str] = None,
                return_node_type: Optional[str] = 'job',
                alpha: float = 0.5) -> Dict[str, float]:
        if personalized:
            ranked_nodes = nx.algorithms.link_analysis.pagerank(self.G, 
                            alpha, {target_node: 1})
        else:
            ranked_nodes = nx.algorithms.link_analysis.pagerank(self.G, 
                                alpha)
        if return_node_type is not None:
            if return_node_type == 'job':
                ranked_nodes = {key:value for key, value in ranked_nodes.items() if ':' in key}
            elif return_node_type == 'candidate':
                ranked_nodes = {key:value for key, value in ranked_nodes.items() if 'candidate' in key}
            elif return_node_type == 'employer':
                ranked_nodes = {key:value for key, value in ranked_nodes.items() if ':' not in key and 'candidate' not in key}

        ranked_nodes = {key:value for key, value in sorted(ranked_nodes.items(), key = lambda x: x[1], reverse = True)}
        return ranked_nodes        
        
    def search(self, keywords: str) -> list:
        results = []
        processor = lambda x: x.lower().translate(str.maketrans('', '', string.punctuation)).split()
        keywords = set(processor(keywords))
        for n in self.G:
            if self.G.nodes[n]['node_type'] == 'candidate':
                continue
            elif self.G.nodes[n]['node_type'] == 'job':
                job_keywords = self.G.nodes[n]['keywords']
                if len(keywords.intersection(set(job_keywords))) >= len(keywords):
                    results.append(n)
            elif self.G.nodes[n]['node_type'] == 'employer':
                employer_keywords = self.G.nodes[n]['keywords']
                if len(keywords.intersection(set(employer_keywords))) >= len(keywords):
                    results.append(n)
        return results

    def _rank_node_with_context(self, target_node: str,
                        context_nodes: List[str],
                        alpha: float,
                        return_node_type:Optional[str] = 'job') -> List[str]:
        personalized = {target_node: 1}
        for node in context_nodes:
            personalized[node] = 1
        ranked_nodes = nx.algorithms.link_analysis.pagerank(self.G,
                        alpha, personalized, )

        if return_node_type is not None:
            if return_node_type == 'job':
                ranked_nodes = {key:value for key, value in ranked_nodes.items() if ':' in key}
            elif return_node_type == 'candidate':
                ranked_nodes = {key:value for key, value in ranked_nodes.items() if 'candidate' in key}
            elif return_node_type == 'employer':
                ranked_nodes = {key:value for key, value in ranked_nodes.items() if ':' not in key and 'candidate' not in key}

        returned_nodes = {key:ranked_nodes[key] for key in context_nodes if key in ranked_nodes.keys()}
        returned_nodes = {key:value for key, value in sorted(returned_nodes.items(), key = lambda x: x[1], reverse = True)}
        return returned_nodes
