from pydantic import BaseModel, ConfigDict

import networkx as nx




class Document(BaseModel):
    text:str
    author:str = "anonimus"




class Graph_preview(BaseModel):
    place:str


class Search_data(BaseModel):
    place:str

class Node(BaseModel):
    type: str | None = None
    description: str | None = None
    source_id: str | None = None
    entity_type: str | None = None
    id: str | None = None

class Link(BaseModel):
    weight: float | None = None
    description: str | None = None
    source_id: str | None = None
    #lehetnének ezek is külön objk
    source: str | None = None
    target: str | None = None

class Graph(BaseModel):
    directed:bool | None = None
    multigraph: bool | None = None
    graph: dict[str, str] | None = None
    nodes:list[Node] | None = None
    links:list[Link] | None = None


def graph2preview(g:nx.Graph):
    pass



class User(BaseModel):
    name:str
    key:str
    documents: list[Graph_preview] = []


class Register_data(BaseModel):
    usr_name:str
