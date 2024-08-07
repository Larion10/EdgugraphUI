from networkx import Graph
import API.KG.llm_api as llm_api
import networkx as nx
import asyncio
import json
import random
import API.KG.promts as promts

#better one? 
# https://arxiv.org/pdf/2405.16506


class Querry():
    def __init__(self, data:nx.Graph, llm:llm_api.AI_API) -> None:
        self.graph = data
        self.llm = llm


    async def get_score(self, querry:str, key:str, desc:str) -> tuple[str, int]:
        s = await self.llm.messenge(
            promt=promts.Querry_Score_Promt.create_promt(querry, key, desc)
        )
        print(s[0])

        score = int(s[0])
        return(key, score)
    
    async def get_community_awnser(self, querry:str, community:nx.Graph) -> tuple[str, int]:
        s = (await self.llm.messenge(
            promts.Querry_ComAwnser_Promt.create_promt(querry, community)
        ))[0]
        res = s.split("<ANSWER>")[1].split("</ANSWER>\n")
        return(res[0], int(res[1].strip()))
    
    async def get_final_awnser(self, querry:str, com_awsners:list[tuple[str, int]]):
        r = promts.Quarry_Final_Awnser.create_promt(querry, [s for s, i in com_awsners])
        p = r[0] + r[1]
        while len(com_awsners) > 1 and len(p) < 1500:
            com_awsners = com_awsners[:len(com_awsners) - 1]
            r = promts.Quarry_Final_Awnser.create_promt(querry, [s for s, i in com_awsners])
            p = r[0] + r[1]
        s = await self.llm.messenge(promts.Quarry_Final_Awnser.create_promt(querry, r))
        return(s)
    

    def strange_dfs(self, l:int, graph:nx.Graph, node:str):
        graph.add_node(node, description= self.graph.nodes[node]["description"])
        
        for nn in self.graph.neighbors(node):
            if ((not (nn in graph.nodes and (node, nn) in graph.edges)) and l - self.graph[node][nn]["weight"] > 0):
                graph.add_node(nn, description= self.graph.nodes[nn]["description"], weight=1)
                graph.add_edge(node, nn, description= self.graph[node][nn]["description"], weight=self.graph[node][nn]["weight"])
                self.strange_dfs(l - self.graph[node][nn]["weight"], graph, nn)
        
        #return(graph)

    def partition(self, q:str, inp:set) -> list[set]:
        p = promts.Querry_ComAwnser_Promt.create_promt(q, self.graph.subgraph(inp))
        if len(p[0] + p[1])  < 1500:
            return([inp])
        else:
            res = []
            p1, p2 = nx.community.kernighan_lin_bisection(self.graph.subgraph(inp))
            for res1 in self.partition(q, p1):
                res.append(res1)
            for res2 in self.partition(q, p2):
                res.append(res2)
            return(res)


    async def get_graph_context(self, querry:str):
        graph = nx.Graph()
        for node, lenght in await asyncio.gather(*[self.get_score(querry, key, self.graph.nodes[key]["description"]) for key in self.graph.nodes]):
            self.strange_dfs(lenght*0.2, graph, node)
        
        #for test
        parts = self.partition(querry, set(graph.nodes))
        print([len(s) for s in parts])
        awnss = await asyncio.gather(*[self.get_community_awnser(querry, graph.subgraph(p)) for p in parts])
        def need(x):
            return(x[1])
        awnss.sort(key=need, reverse=True)
        return (await self.get_final_awnser(querry, awnss))[0]
        

class EDU_Querry(Querry):
    def strange_dfs(self, l:int, graph:nx.Graph, node:str):
        graph.add_node(node, description= self.graph.nodes[node]["description"])
        
        for nn in self.graph.neighbors(node):
            if ((not (nn in graph.nodes and (node, nn) in graph.edges)) and l - self.graph[node][nn]["weight"] > 0 and
                len(promts.EDU_Quarry_question_promt.create_promt(graph)) < 1500):
                graph.add_node(nn, description= self.graph.nodes[nn]["description"], weight=1)
                graph.add_edge(node, nn, description= self.graph[node][nn]["description"], weight=self.graph[node][nn]["weight"])
                self.strange_dfs(l - self.graph[node][nn]["weight"], graph, nn)
        
    async def get_question_and_answers(self, graph) -> tuple[str, list[str]]:
        r = (await self.llm.messenge(
            promts.EDU_Quarry_question_promt.create_promt(graph)
        ))[0]
        print(r)
        r = r.split("<QUESTION>")[1]
        q, a_s= r.split("</QUESTION>")[0], r.split("</QUESTION>")[1].split("</ANSWER>")[:3]
        for a in range(len(a_s)):
            print(a_s[a])
            a_s[a] = a_s[a].split("<ANSWER>")[1]

        return(q, a_s)
    

    async def get_graph_context(self):
        graph = nx.Graph()

        self.strange_dfs(30, graph, random.choice(list(self.graph.nodes)))

        return(await self.get_question_and_answers(graph))
    
    async def point_for_answer(self, q, a_s, answer):
        return((await self.llm.messenge(
            promts.EDU_ANSWER_point_promt.create_promt(q, a_s, answer)
        ))[0])



"""q = Querry(nx.node_link_graph(json.load(open("test_graph.json", "r"))), "")
async def need2():
    print(await q.get_graph_context("  "))


asyncio.run(need2())"""
