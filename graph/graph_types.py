from dataclasses import dataclass, field

from models.knowledge_edge import KnowledgeEdge
from models.knowledge_node import KnowledgeNode


class NodeType:
    PROJECT = "project"
    FACT = "fact"
    ENTITY = "entity"
    ACTOR = "actor"
    PROCESS = "process"
    RULE = "rule"
    REQUIREMENT = "requirement"
    DECISION = "decision"
    RISK = "risk"
    INTEGRATION = "integration"
    ARTIFACT = "artifact"
    SOURCE = "source"
    UNKNOWN = "unknown"


class EdgeType:
    RELATES_TO = "relates_to"
    PARTICIPATES_IN = "participates_in"
    DEPENDS_ON = "depends_on"
    IMPLEMENTS = "implements"
    DISCUSSED_IN = "discussed_in"
    AFFECTS = "affects"
    CONTRADICTS = "contradicts"
    SUPERSEDES = "supersedes"
    DERIVED_FROM = "derived_from"
    BELONGS_TO = "belongs_to"
    DOCUMENTS = "documents"


@dataclass
class KnowledgeGraph:
    nodes: dict[str, KnowledgeNode] = field(default_factory=dict)
    edges: list[KnowledgeEdge] = field(default_factory=list)

    def add_node(self, node: KnowledgeNode):
        self.nodes[node.id] = node

    def add_edge(self, edge: KnowledgeEdge):
        if edge.from_node_id in self.nodes and edge.to_node_id in self.nodes:
            self.edges.append(edge)

    def get_node(self, node_id: str) -> KnowledgeNode | None:
        return self.nodes.get(node_id)

    def find_nodes(self, query: str = "", node_type: str | None = None) -> list[KnowledgeNode]:
        normalized_query = (query or "").strip().lower()

        result = []

        for node in self.nodes.values():
            if node_type and node.node_type != node_type:
                continue

            if not normalized_query:
                result.append(node)
                continue

            haystack = f"{node.title} {node.description}".lower()
            if normalized_query in haystack:
                result.append(node)

        return result

    def related_edges(self, node_id: str) -> list[KnowledgeEdge]:
        return [
            edge
            for edge in self.edges
            if edge.from_node_id == node_id or edge.to_node_id == node_id
        ]

    def related_nodes(self, node_id: str) -> list[KnowledgeNode]:
        related_ids = set()

        for edge in self.related_edges(node_id):
            if edge.from_node_id != node_id:
                related_ids.add(edge.from_node_id)
            if edge.to_node_id != node_id:
                related_ids.add(edge.to_node_id)

        return [self.nodes[node_id] for node_id in related_ids if node_id in self.nodes]

    def stats(self) -> dict[str, int]:
        by_type: dict[str, int] = {}

        for node in self.nodes.values():
            by_type[node.node_type] = by_type.get(node.node_type, 0) + 1

        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            **by_type,
        }
