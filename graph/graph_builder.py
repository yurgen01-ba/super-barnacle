from __future__ import annotations

from typing import Any, Iterable

from graph.graph_types import EdgeType, KnowledgeGraph, NodeType
from graph.node_normalizer import normalize_to_node
from models.knowledge_edge import KnowledgeEdge
from models.knowledge_node import KnowledgeNode


def _safe_call(obj: Any, method_names: list[str]) -> list[Any]:
    if obj is None:
        return []

    for method_name in method_names:
        method = getattr(obj, method_name, None)
        if callable(method):
            try:
                result = method()
                if result is None:
                    return []
                if isinstance(result, list):
                    return result
                if isinstance(result, tuple):
                    return list(result)
                return list(result)
            except TypeError:
                continue
            except Exception:
                return []

    return []


def _add_nodes_from_repository(
    graph: KnowledgeGraph,
    repository: Any,
    node_type: str,
    source: str,
    method_names: list[str],
) -> list[KnowledgeNode]:
    items = _safe_call(repository, method_names)
    nodes: list[KnowledgeNode] = []

    for idx, item in enumerate(items, start=1):
        node = normalize_to_node(
            item=item,
            node_type=node_type,
            source=source,
            fallback_index=idx,
        )
        graph.add_node(node)
        nodes.append(node)

    return nodes


def _add_keyword_edges(graph: KnowledgeGraph, from_nodes: Iterable[KnowledgeNode], to_nodes: Iterable[KnowledgeNode]):
    for left in from_nodes:
        left_text = f"{left.title} {left.description}".lower()

        for right in to_nodes:
            if left.id == right.id:
                continue

            right_title = right.title.strip().lower()
            if not right_title or len(right_title) < 3:
                continue

            if right_title in left_text:
                graph.add_edge(
                    KnowledgeEdge(
                        id=f"edge:{left.id}:{EdgeType.RELATES_TO}:{right.id}",
                        from_node_id=left.id,
                        to_node_id=right.id,
                        relationship_type=EdgeType.RELATES_TO,
                        confidence=0.45,
                        source="keyword_match",
                    )
                )


class GraphBuilder:
    def __init__(
        self,
        fact_repository: Any | None = None,
        entity_repository: Any | None = None,
        actor_repository: Any | None = None,
        process_repository: Any | None = None,
        relationship_repository: Any | None = None,
        domain_model_repository: Any | None = None,
        ontology_repository: Any | None = None,
    ):
        self.fact_repository = fact_repository
        self.entity_repository = entity_repository
        self.actor_repository = actor_repository
        self.process_repository = process_repository
        self.relationship_repository = relationship_repository
        self.domain_model_repository = domain_model_repository
        self.ontology_repository = ontology_repository

    def build(self) -> KnowledgeGraph:
        graph = KnowledgeGraph()

        facts = _add_nodes_from_repository(
            graph, self.fact_repository, NodeType.FACT, "fact_repository",
            ["list_facts", "get_facts", "get_all", "list_all", "list", "all"],
        )

        entities = _add_nodes_from_repository(
            graph, self.entity_repository, NodeType.ENTITY, "entity_repository",
            ["list_entities", "get_entities", "get_all", "list_all", "list", "all"],
        )

        actors = _add_nodes_from_repository(
            graph, self.actor_repository, NodeType.ACTOR, "actor_repository",
            ["list_actors", "get_actors", "get_all", "list_all", "list", "all"],
        )

        processes = _add_nodes_from_repository(
            graph, self.process_repository, NodeType.PROCESS, "process_repository",
            ["list_processes", "get_processes", "get_all", "list_all", "list", "all"],
        )

        domain_objects = _add_nodes_from_repository(
            graph, self.domain_model_repository, NodeType.ENTITY, "domain_model_repository",
            ["list_domain_objects", "get_domain_objects", "get_all", "list_all", "list", "all"],
        )

        ontology_nodes = _add_nodes_from_repository(
            graph, self.ontology_repository, NodeType.UNKNOWN, "ontology_repository",
            ["list_terms", "get_terms", "get_all", "list_all", "list", "all"],
        )

        _add_keyword_edges(graph, facts, entities + actors + processes + domain_objects)
        _add_keyword_edges(graph, processes, entities + actors + domain_objects)
        _add_keyword_edges(graph, entities + domain_objects, actors + processes)
        _add_keyword_edges(graph, ontology_nodes, facts + entities + actors + processes)

        return graph
