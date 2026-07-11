from __future__ import annotations

from dataclasses import dataclass, field

from graph.evidence_collector import EvidenceCollector
from graph.graph_repository import GraphRepository
from graph.graph_types import KnowledgeGraph
from models.knowledge_edge import KnowledgeEdge
from models.knowledge_node import KnowledgeNode


@dataclass(slots=True)
class NodeProfile:
    node: KnowledgeNode
    related_nodes: list[KnowledgeNode] = field(default_factory=list)
    related_edges: list[KnowledgeEdge] = field(default_factory=list)

    def to_context(self) -> str:
        lines: list[str] = []

        lines.append(f"[{self.node.node_type}] {self.node.title}")

        if self.node.description:
            lines.append(f"Description: {self.node.description}")

        lines.append(f"Status: {self.node.status}")
        lines.append(f"Confidence: {self.node.confidence}")
        lines.append(f"Source: {self.node.source}")

        if self.related_nodes:
            lines.append("Related nodes:")
            for related in self.related_nodes:
                lines.append(f"- [{related.node_type}] {related.title}")

        return "\n".join(lines)


@dataclass(slots=True)
class GraphContext:
    query: str
    stats: dict[str, int]
    profiles: list[NodeProfile] = field(default_factory=list)
    evidence_summary: str = ""

    def to_prompt_context(self) -> str:
        lines: list[str] = []

        lines.append("PROJECT KNOWLEDGE GRAPH CONTEXT")
        lines.append("")
        lines.append(f"User query: {self.query}")
        lines.append("")
        lines.append("Graph statistics:")
        for key, value in sorted(self.stats.items()):
            lines.append(f"- {key}: {value}")

        lines.append("")
        lines.append("Matched knowledge nodes:")

        if not self.profiles:
            lines.append("- No matching graph nodes found.")
        else:
            for idx, profile in enumerate(self.profiles, start=1):
                lines.append("")
                lines.append(f"## Node {idx}")
                lines.append(profile.to_context())

        if self.evidence_summary:
            lines.append("")
            lines.append(self.evidence_summary)

        return "\n".join(lines)


class GraphQueryEngine:
    def __init__(self, graph_repository: GraphRepository):
        self.graph_repository = graph_repository
        self.evidence_collector = EvidenceCollector(graph_repository)

    def get_context(
        self,
        query: str,
        node_type: str | None = None,
        limit: int = 10,
        related_limit: int = 8,
        refresh: bool = False,
    ) -> GraphContext:
        graph = self.graph_repository.get_graph(refresh=refresh)
        nodes = self._rank_nodes(graph, query, node_type, limit)

        profiles = [
            self.get_node_profile(node.id, related_limit=related_limit, graph=graph)
            for node in nodes
        ]

        evidence_summary = self.evidence_collector.build_evidence_summary(nodes)

        return GraphContext(
            query=query,
            stats=graph.stats(),
            profiles=profiles,
            evidence_summary=evidence_summary,
        )

    def get_node_profile(self, node_id: str, related_limit: int = 12, graph: KnowledgeGraph | None = None) -> NodeProfile:
        graph = graph or self.graph_repository.get_graph()
        node = graph.get_node(node_id)

        if node is None:
            raise ValueError(f"Knowledge node not found: {node_id}")

        return NodeProfile(
            node=node,
            related_nodes=graph.related_nodes(node_id)[:related_limit],
            related_edges=graph.related_edges(node_id),
        )

    def search_nodes(self, query: str, node_type: str | None = None, limit: int = 20) -> list[KnowledgeNode]:
        graph = self.graph_repository.get_graph()
        return self._rank_nodes(graph, query, node_type, limit)

    def _rank_nodes(self, graph: KnowledgeGraph, query: str, node_type: str | None, limit: int) -> list[KnowledgeNode]:
        normalized_query = (query or "").strip().lower()

        if not normalized_query:
            return graph.find_nodes(node_type=node_type)[:limit]

        candidates = graph.find_nodes(node_type=node_type)
        query_terms = [
            term
            for term in normalized_query.replace("/", " ").replace("-", " ").split()
            if len(term) >= 3
        ]

        scored: list[tuple[float, KnowledgeNode]] = []

        for node in candidates:
            text = f"{node.title} {node.description}".lower()
            score = 0.0

            if normalized_query in node.title.lower():
                score += 5.0
            elif normalized_query in text:
                score += 3.0

            for term in query_terms:
                if term in node.title.lower():
                    score += 2.0
                elif term in text:
                    score += 1.0

            score += min(len(graph.related_nodes(node.id)), 10) * 0.1
            score += float(node.confidence or 0)

            if score > 0:
                scored.append((score, node))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [node for _, node in scored[:limit]]
