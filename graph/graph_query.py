from dataclasses import dataclass

from graph.graph_repository import GraphRepository
from models.knowledge_node import KnowledgeNode


@dataclass(slots=True)
class GraphSearchResult:
    node: KnowledgeNode
    related_nodes: list[KnowledgeNode]
    score: float


class GraphRetriever:
    """
    Graph-aware retriever for AI context.

    This is the first version:
    - find matching nodes;
    - expand one hop;
    - produce structured context for LLM prompt builders.
    """

    def __init__(self, graph_repository: GraphRepository):
        self.graph_repository = graph_repository

    def search(
        self,
        query: str,
        node_type: str | None = None,
        limit: int = 8,
        related_limit: int = 6,
    ) -> list[GraphSearchResult]:
        matched_nodes = self.graph_repository.find_nodes(
            query=query,
            node_type=node_type,
            limit=limit,
        )

        results: list[GraphSearchResult] = []

        for node in matched_nodes:
            related = self.graph_repository.related_nodes(node.id, limit=related_limit)
            score = self._score_node(query, node, related)

            results.append(
                GraphSearchResult(
                    node=node,
                    related_nodes=related,
                    score=score,
                )
            )

        return sorted(results, key=lambda item: item.score, reverse=True)

    def build_context(
        self,
        query: str,
        node_type: str | None = None,
        limit: int = 8,
        related_limit: int = 6,
    ) -> str:
        stats = self.graph_repository.stats()
        results = self.search(
            query=query,
            node_type=node_type,
            limit=limit,
            related_limit=related_limit,
        )

        lines: list[str] = []

        lines.append("PROJECT KNOWLEDGE GRAPH CONTEXT")
        lines.append("")
        lines.append("Graph statistics:")
        for key, value in stats.items():
            lines.append(f"- {key}: {value}")

        lines.append("")
        lines.append("Relevant nodes:")

        if not results:
            lines.append("- No directly matching graph nodes found.")
            return "\n".join(lines)

        for idx, result in enumerate(results, start=1):
            node = result.node

            lines.append("")
            lines.append(f"{idx}. [{node.node_type}] {node.title}")
            if node.description:
                lines.append(f"   Description: {node.description}")
            lines.append(f"   Confidence: {node.confidence}")
            lines.append(f"   Status: {node.status}")
            lines.append(f"   Source: {node.source}")

            if result.related_nodes:
                lines.append("   Related:")
                for related in result.related_nodes:
                    lines.append(f"   - [{related.node_type}] {related.title}")

        return "\n".join(lines)

    @staticmethod
    def _score_node(query: str, node: KnowledgeNode, related_nodes: list[KnowledgeNode]) -> float:
        normalized_query = (query or "").lower()
        title = node.title.lower()
        description = node.description.lower()

        score = 0.0

        if normalized_query and normalized_query in title:
            score += 3.0

        if normalized_query and normalized_query in description:
            score += 1.5

        score += min(len(related_nodes), 5) * 0.2
        score += node.confidence

        return score
