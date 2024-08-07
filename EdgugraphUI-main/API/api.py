
import json
import networkx as nx
import random

from API.data_structures import *
import API.KG.graph_extractor as extractor
import API.KG.llm_api as llms
from API.KG.querry import Querry
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
    print(type(documents[0]))
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





async def question(graph:Graph_preview, querry:str):
    #just change the system prompt (will be awailable after parametarising querry)
    return (await querry(graph, querry))


async def test(graph:Graph_preview):
    #TODO just chenge the system prompt (will be awailable after parametarising querry)
    q = (await querry(graph, ""))["awnser"]
    #TODO generate the awnser as well
    a = (await querry(graph, "q"))["awnser"] #you have to controll the student's awnser locally.
    return ({
        "question": q,
        "awnser": a
    })


