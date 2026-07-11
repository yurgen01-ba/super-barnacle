from __future__ import annotations

from graph.graph_repository import GraphRepository
from models.knowledge_node import KnowledgeNode


class EvidenceCollector:
    """
    Builds evidence and confidence summaries from graph nodes.

    This is not persisted evidence yet.
    It exposes source/confidence/status from KnowledgeNodes.
    """

    def __init__(self, graph_repository: GraphRepository):
        self.graph_repository = graph_repository

    def build_evidence_summary(self, nodes: list[KnowledgeNode]) -> str:
        lines: list[str] = []

        lines.append("Evidence and confidence:")

        if not nodes:
            lines.append("- No evidence nodes found.")
            return "\n".join(lines)

        for node in nodes:
            lines.append(
                f"- [{node.node_type}] {node.title} | "
                f"source={node.source or 'unknown'} | "
                f"confidence={node.confidence} | "
                f"status={node.status}"
            )

        return "\n".join(lines)
