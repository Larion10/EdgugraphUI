import logging
import numbers
import re
import traceback
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import networkx as nx
import tiktoken
import asyncio


from API.KG.llm_api import AI_API 
import API.KG.promts as promts

DEFAULT_TUPLE_DELIMITER = "<|>"
DEFAULT_RECORD_DELIMITER = "##"
DEFAULT_COMPLETION_DELIMITER = "<|COMPLETE|>"
DEFAULT_ENTITY_TYPES = ["organization", "person", "geo", "event"]



import html
import re
from typing import Any
import streamlit as st

def clean_str(input: Any) -> str:
    """Clean an input string by removing HTML escapes, control characters, and other unwanted characters."""
    # If we get non-string input, just give it back
    if not isinstance(input, str):
        return input

    result = html.unescape(input.strip())
    # https://stackoverflow.com/questions/4324790/removing-control-characters-from-a-string-in-python
    return re.sub(r"[\x00-\x1f\x7f-\x9f]", "", result)


def textsplitter(txt:str, l:int, u:int) -> list[str]:
    i = 0
    res = []
    while(i + l < len(txt)):
        res.append(txt[i : i + l])
        i += l - u
    return(res)



@dataclass
class GraphExtractionResult:
    """Unipartite graph extraction result class definition."""

    output: nx.Graph
    source_docs: dict[Any, Any]


class GraphExtractor:
    """Unipartite graph extractor class definition."""

    _llm: AI_API
    _join_descriptions: bool
    _tuple_delimiter_key: str
    _record_delimiter_key: str
    _entity_types_key: str
    _input_text_key: str
    _completion_delimiter_key: str
    _entity_name_key: str
    _input_descriptions_key: str
    _summarization_prompt: str
    _max_gleanings: int

    def __init__(
        self,
        llm_invoker: AI_API,
        join_descriptions=True,             #TODO: with LLM?
        encoding_model: str | None = None,
        max_gleanings: int | None = None,
        on_error = None # function 
    ):
        """Init method definition."""
        self._llm = llm_invoker
        self._join_descriptions = join_descriptions
        self._input_text_key = "input_text"
        self._tuple_delimiter_key = "tuple_delimiter"
        self._record_delimiter_key = "record_delimiter"
        self._completion_delimiter_key = "completion_delimiter"
        self._entity_types_key = "entity_types"


        self._max_gleanings = (
            max_gleanings
            if max_gleanings is not None
            else 0
        )
        self._on_error = on_error or (lambda _e, _s, _d: print(_e))


    async def __call__(
        self, texts: list[str], entity_types: list[str] | None = None, language:str = "english") -> GraphExtractionResult:
        """Call method definition."""
        
        all_records: dict[int, str] = {doc_id: result for doc_id, result in enumerate(await asyncio.gather(*[self._process_document(text, 
                                                    ",".join(entity_types
                                                            or DEFAULT_ENTITY_TYPES),
                                                    language) for text in texts]))}
        
        source_doc_map: dict[int, str] = {doc_id : text for doc_id, text in enumerate(texts)}
        
            

        output = await self._process_results(
            all_records, DEFAULT_TUPLE_DELIMITER, DEFAULT_RECORD_DELIMITER)

        return GraphExtractionResult(
            output=output,
            source_docs=source_doc_map,
        )

    async def _process_document(
        self, text: str, entity_types: list[str], language:str
    ) -> str:
        response = await self._llm.messenge(
            promts.Relationship_Generation_Promt.create_promt(entity_types, 
                                                              language,
                                                              DEFAULT_TUPLE_DELIMITER,
                                                              DEFAULT_RECORD_DELIMITER,
                                                              DEFAULT_COMPLETION_DELIMITER,
                                                              text),
        )
        
        results = response[0]
        hist = response[1]

        # Repeat to ensure we maximize entity count
        for i in range(self._max_gleanings):
            print(self._max_gleanings)

            glean_response = await self._llm.messenge(
                promts.Continue_Promt.create_promt(),
                name=f"extract-continuation-{i}",
                history=hist,
            )
            print(glean_response[0])
            results += glean_response[0]
            hist += glean_response[1]

            # if this is the final, don't bother updating the continuation flag
            if i >= self._max_gleanings - 1:
                break

            continuation = await self._llm.messenge(
                promts.Loop_Promt.create_promt(),
                name=f"extract-loopcheck-{i}",
                history=hist,
                #TODO   model_parameters=self._loop_args, 
            )
            if continuation[0] != "YES":
                break

        
        return results.split(DEFAULT_COMPLETION_DELIMITER)[0]

    async def _process_results(
        self,
        results: dict[int, str],
        tuple_delimiter: str,
        record_delimiter: str,
    ) -> nx.Graph:
        """Parse the result string to create an undirected unipartite graph.

        Args:
            - results - dict of results from the extraction chain
            - tuple_delimiter - delimiter between tuples in an output record, default is '<|>'
            - record_delimiter - delimiter between records, default is '##'
        Returns:
            - output - unipartite graph in graphML format
        """
        graph = nx.Graph()
        for source_doc_id, extracted_data in results.items():
            records = [r.strip() for r in extracted_data.split(record_delimiter)]

            for record in records:
                record = re.sub(r"^\(|\)$", "", record.strip())
                record_attributes = record.split(tuple_delimiter)

                if record_attributes[0] == '"entity"' and len(record_attributes) >= 4:
                    # add this record as a node in the G
                    entity_name = clean_str(record_attributes[1].upper())
                    entity_type = clean_str(record_attributes[2].upper())
                    entity_description = clean_str(record_attributes[3])

                    if entity_name in graph.nodes():
                        node = graph.nodes[entity_name]
                        if self._join_descriptions:
                            node["description"] = "\n".join(
                                list({
                                    *_unpack_descriptions(node),
                                    entity_description,
                                })
                            )
                        else:
                            if len(entity_description) > len(node["description"]):
                                node["description"] = entity_description
                        node["source_id"] = ", ".join(
                            list({
                                *_unpack_source_ids(node),
                                str(source_doc_id),
                            })
                        )
                        node["entity_type"] = (
                            entity_type if entity_type != "" else node["entity_type"]
                        )
                    else:
                        graph.add_node(
                            entity_name,
                            type=entity_type,
                            description=entity_description,
                            source_id=str(source_doc_id),
                        )

                if (
                    record_attributes[0] == '"relationship"'
                    and len(record_attributes) >= 5
                ):
                    # add this record as edge
                    source = clean_str(record_attributes[1].upper())
                    target = clean_str(record_attributes[2].upper())
                    edge_description = clean_str(record_attributes[3])
                    edge_source_id = clean_str(str(source_doc_id))
                    weight = 1
                    if (record_attributes[-1] in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "8", "9", "10"]):
                        weight = (10 - float(record_attributes[-1]))
                    
                    if source not in graph.nodes():
                        graph.add_node(
                            source,
                            type="",
                            description="",
                            source_id=edge_source_id,
                        )
                    if target not in graph.nodes():
                        graph.add_node(
                            target,
                            type="",
                            description="",
                            source_id=edge_source_id,
                        )
                    if graph.has_edge(source, target):
                        edge_data = graph.get_edge_data(source, target)
                        if edge_data is not None:
                            weight += edge_data["weight"]
                            if self._join_descriptions:
                                edge_description = "\n".join(
                                    list({
                                        *_unpack_descriptions(edge_data),
                                        edge_description,
                                    })
                                )
                            edge_source_id = ", ".join(
                                list({
                                    *_unpack_source_ids(edge_data),
                                    str(source_doc_id),
                                })
                            )
                    graph.add_edge(
                        source,
                        target,
                        weight=weight,
                        description=edge_description,
                        source_id=edge_source_id,
                    )

        return graph


def _unpack_descriptions(data: Mapping) -> list[str]:
    value = data.get("description", None)
    return [] if value is None else value.split("\n")


def _unpack_source_ids(data: Mapping) -> list[str]:
    value = data.get("source_id", None)
    return [] if value is None else value.split(", ")
