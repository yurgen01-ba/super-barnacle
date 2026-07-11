from __future__ import annotations

from typing import Any

from graph.graph_builder import GraphBuilder
from graph.graph_types import KnowledgeGraph
from models.knowledge_node import KnowledgeNode


class GraphRepository:
    """
    Public read API for Project Brain Knowledge Graph.

    New AI functionality should depend on GraphRepository instead of directly
    depending on FactRepository, EntityRepository, ActorRepository or ProcessRepository.
    """

    def __init__(self, builder: GraphBuilder | None = None, **repositories: Any):
        self.builder = builder or GraphBuilder(**repositories)
        self._graph_cache: KnowledgeGraph | None = None

    def get_graph(self, refresh: bool = False) -> KnowledgeGraph:
        if self._graph_cache is None or refresh:
            self._graph_cache = self.builder.build()
        return self._graph_cache

    def stats(self, refresh: bool = False) -> dict[str, int]:
        return self.get_graph(refresh=refresh).stats()

    def find_nodes(
        self,
        query: str = "",
        node_type: str | None = None,
        limit: int = 20,
        refresh: bool = False,
    ) -> list[KnowledgeNode]:
        nodes = self.get_graph(refresh=refresh).find_nodes(query=query, node_type=node_type)
        return nodes[:limit]

    def get_node(self, node_id: str, refresh: bool = False) -> KnowledgeNode | None:
        return self.get_graph(refresh=refresh).get_node(node_id)

    def related_nodes(self, node_id: str, limit: int = 20, refresh: bool = False) -> list[KnowledgeNode]:
        nodes = self.get_graph(refresh=refresh).related_nodes(node_id)
        return nodes[:limit]

    def related_edges(self, node_id: str, refresh: bool = False):
        return self.get_graph(refresh=refresh).related_edges(node_id)
