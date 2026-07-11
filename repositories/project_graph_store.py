from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from models.knowledge_edge import KnowledgeEdge
from models.knowledge_node import KnowledgeNode


@dataclass
class ProjectGraphSnapshot:
    nodes: dict[str, KnowledgeNode] = field(default_factory=dict)
    edges: list[KnowledgeEdge] = field(default_factory=list)

    def add_node(self, node: KnowledgeNode):
        self.nodes[node.id] = node

    def add_edge(self, edge: KnowledgeEdge):
        if edge.from_node_id in self.nodes and edge.to_node_id in self.nodes:
            if not any(existing.id == edge.id for existing in self.edges):
                self.edges.append(edge)

    def stats(self) -> dict[str, int]:
        by_type: dict[str, int] = {}

        for node in self.nodes.values():
            by_type[node.node_type] = by_type.get(node.node_type, 0) + 1

        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            **by_type,
        }


class ProjectGraphStore:
    """
    Runtime Project Graph store.

    This version is compatible with the persistent repository, but it also works
    when persistence is temporarily unavailable.
    """

    def __init__(self):
        self._graphs: dict[str, ProjectGraphSnapshot] = {}

    def get_graph(self, project_id: str = "default", hydrate: bool = True) -> ProjectGraphSnapshot:
        if project_id not in self._graphs:
            self._graphs[project_id] = ProjectGraphSnapshot()
            if hydrate:
                self.hydrate(project_id)
        return self._graphs[project_id]

    def hydrate(self, project_id: str = "default") -> ProjectGraphSnapshot:
        """
        Load persisted graph into runtime memory.

        This method is required by GraphRetrieverV2.
        """
        graph = self._graphs.setdefault(project_id, ProjectGraphSnapshot())
        graph.nodes.clear()
        graph.edges.clear()

        try:
            from repositories.persistent_project_graph_repository import persistent_project_graph_repository

            for node in persistent_project_graph_repository.load_nodes(project_id):
                graph.nodes[node.id] = node

            for edge in persistent_project_graph_repository.load_edges(project_id):
                if edge.from_node_id in graph.nodes and edge.to_node_id in graph.nodes:
                    if not any(existing.id == edge.id for existing in graph.edges):
                        graph.edges.append(edge)

        except Exception:
            # Keep app usable even if SQLite/persistence is temporarily broken.
            pass

        return graph

    def save_node(self, node: KnowledgeNode, project_id: str = "default") -> KnowledgeNode:
        graph = self.get_graph(project_id, hydrate=False)
        graph.nodes[node.id] = node

        try:
            from repositories.persistent_project_graph_repository import persistent_project_graph_repository

            persistent_project_graph_repository.save_node(node, project_id)
        except Exception:
            pass

        return node

    def save_edge(self, edge: KnowledgeEdge, project_id: str = "default") -> KnowledgeEdge:
        graph = self.get_graph(project_id, hydrate=False)

        if edge.from_node_id in graph.nodes and edge.to_node_id in graph.nodes:
            if not any(existing.id == edge.id for existing in graph.edges):
                graph.edges.append(edge)

            try:
                from repositories.persistent_project_graph_repository import persistent_project_graph_repository

                persistent_project_graph_repository.save_edge(edge, project_id)
            except Exception:
                pass

        return edge

    def save_actor(self, title: str, description: str = "", **metadata: Any) -> KnowledgeNode:
        return self.save_node(
            KnowledgeNode(
                id=f"actor:{uuid4()}",
                node_type="actor",
                title=title,
                description=description,
                metadata=metadata,
                source="project_graph_store",
            )
        )

    def save_process(self, title: str, description: str = "", **metadata: Any) -> KnowledgeNode:
        return self.save_node(
            KnowledgeNode(
                id=f"process:{uuid4()}",
                node_type="process",
                title=title,
                description=description,
                metadata=metadata,
                source="project_graph_store",
            )
        )

    def save_entity(self, title: str, description: str = "", **metadata: Any) -> KnowledgeNode:
        return self.save_node(
            KnowledgeNode(
                id=f"entity:{uuid4()}",
                node_type="entity",
                title=title,
                description=description,
                metadata=metadata,
                source="project_graph_store",
            )
        )

    def save_fact(self, title: str, description: str = "", **metadata: Any) -> KnowledgeNode:
        return self.save_node(
            KnowledgeNode(
                id=f"fact:{uuid4()}",
                node_type="fact",
                title=title,
                description=description,
                metadata=metadata,
                source="project_graph_store",
            )
        )

    def find(self, query: str = "", node_type: str | None = None, project_id: str = "default") -> list[KnowledgeNode]:
        graph = self.get_graph(project_id)
        q = (query or "").lower().strip()
        nodes = list(graph.nodes.values())

        if node_type:
            nodes = [node for node in nodes if node.node_type == node_type]

        if q:
            nodes = [
                node
                for node in nodes
                if q in f"{node.title} {node.description}".lower()
            ]

        return nodes

    def get_neighbors(self, node_id: str, project_id: str = "default") -> list[KnowledgeNode]:
        graph = self.get_graph(project_id)
        neighbor_ids = set()

        for edge in graph.edges:
            if edge.from_node_id == node_id:
                neighbor_ids.add(edge.to_node_id)
            elif edge.to_node_id == node_id:
                neighbor_ids.add(edge.from_node_id)

        return [
            graph.nodes[node_id]
            for node_id in neighbor_ids
            if node_id in graph.nodes
        ]


project_graph_store = ProjectGraphStore()
