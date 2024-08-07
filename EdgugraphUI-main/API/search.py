import networkx as nx
from API.data_structures import Graph_preview, Search_data

import random
import copy

class Search_Graph(nx.Graph):
    def add_node(self, node_for_adding:Graph_preview):
        rel_scores = [(self.get_topic_score(n), n) for n in self.nodes]
        if (len(rel_scores) > 5):

            def k(x):
                return(x[0])
            
            rel_scores.sort(key=k)
            rel_scores = rel_scores[:5]
        super().add_node(node_for_adding)
        
        for val, nn in rel_scores:
            self.add_edge(nn, node_for_adding, weight=self.get_coherence_score(node_for_adding, nn))

    
    def search(self, querry:Search_data) -> list[Graph_preview]:
        #scores
        rel_scores = {n: self.get_relevance_score(querry, n) for n in self.nodes}
        n_rel_scores = copy.deepcopy(rel_scores)

        #gauss
        for n in self.nodes:
            for nn in self.neighbors(n):
                n_rel_scores[nn] += rel_scores[n] * 0.2
            n_rel_scores[n] *= 0.8
        
        res = [(v, n) for n, v in n_rel_scores.items()]
        def k(x):
            return(x[0])
        res.sort(key=k)

        return([n for v, n in res])




    def get_topic_score(self, new_node:Graph_preview, other:Graph_preview) -> int:
        return(random.randint(0, 10))


    def get_coherence_score(self, new_node:Graph_preview, other:Graph_preview) -> int:
        return(random.randint(0, 10))
    

    def get_relevance_score(self, querry:Search_data, node:Graph_preview) -> int:
        return(random.randint(0, 10))
    
