
import json
import networkx as nx
import random

from API.data_structures import *
import API.KG.graph_extractor as extractor
import API.KG.llm_api as llms
from API.KG.querry import Querry, EDU_Querry
from API.search import Search_Graph






#search object
SEARCH_GRAPH = Search_Graph()






async def search(search_data: Search_data) -> list[Graph_preview]:
    res = SEARCH_GRAPH.search(search_data)
    return(res)




#GRAPH CREATION
async def generate_graph(documents:list[Document], lenght:int = 600, overlap:int = 100) -> Graph:
    #TODO: test
    #TODO: parameterise
    creator = extractor.GraphExtractor(llms.AI71_api())
    txts = []
    for doc in documents:
        for txt in extractor.textsplitter(doc, lenght, overlap):
            txts.append(txt)
    g = (await creator(txts)).output
    
    return(g)



async def querry(graph:Graph_preview, querry:str):
    #TODO: Arimetric
    #TODO: parameterise
    q = Querry(graph, llms.AI71_api())
    res = await q.get_graph_context(querry)
    return({"awnser": res})






async def question(graph:Graph_preview):
    q = EDU_Querry(graph, llms.AI71_api())

    res = await q.get_graph_context()
    return(res)


async def answer_point(question, a_s, answer):
    q = EDU_Querry(nx.Graph(), llms.AI71_api())

    res = await q.point_for_answer(question, a_s, answer)
    return(res)


