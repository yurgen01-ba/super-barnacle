from __future__ import annotations

from dataclasses import dataclass, field

from graph.graph_repository import GraphRepository
from models.knowledge_edge import KnowledgeEdge
from models.knowledge_node import KnowledgeNode


@dataclass(slots=True)
class KnowledgeNodeProfile:
    node: KnowledgeNode
    neighbors: list[KnowledgeNode] = field(default_factory=list)
    edges: list[KnowledgeEdge] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "node": self.node.to_dict(),
            "neighbors": [node.to_dict() for node in self.neighbors],
            "edges": [edge.to_dict() for edge in self.edges],
        }

    def to_markdown(self) -> str:
        lines: list[str] = []

        lines.append(f"# {self.node.title}")
        lines.append("")
        lines.append(f"- Type: {self.node.node_type}")
        lines.append(f"- Status: {self.node.status}")
        lines.append(f"- Confidence: {self.node.confidence}")
        lines.append(f"- Source: {self.node.source}")

        if self.node.description:
            lines.append("")
            lines.append("## Description")
            lines.append(self.node.description)

        lines.append("")
        lines.append("## Neighbors")
        if not self.neighbors:
            lines.append("- None")
        else:
            for node in self.neighbors:
                lines.append(f"- [{node.node_type}] {node.title}")

        lines.append("")
        lines.append("## Relationships")
        if not self.edges:
            lines.append("- None")
        else:
            for edge in self.edges:
                lines.append(f"- {edge.from_node_id} --{edge.relationship_type}--> {edge.to_node_id}")

        return "\n".join(lines)


class KnowledgeInspector:
    """
    Backend API for future Knowledge Graph Inspector UI.
    """

    def __init__(self, graph_repository: GraphRepository):
        self.graph_repository = graph_repository

    def get_profile(self, node_id: str) -> KnowledgeNodeProfile:
        graph = self.graph_repository.get_graph()
        node = graph.get_node(node_id)

        if node is None:
            raise ValueError(f"Knowledge node not found: {node_id}")

        return KnowledgeNodeProfile(
            node=node,
            neighbors=graph.related_nodes(node_id),
            edges=graph.related_edges(node_id),
        )

    def search_profiles(self, query: str, limit: int = 10) -> list[KnowledgeNodeProfile]:
        nodes = self.graph_repository.find_nodes(query=query, limit=limit)
        return [self.get_profile(node.id) for node in nodes]
