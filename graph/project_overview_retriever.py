from __future__ import annotations

from graph.graph_repository import GraphRepository
from graph.graph_types import NodeType
from models.knowledge_node import KnowledgeNode


class ProjectOverviewRetriever:
    """
    Deterministic project overview retriever.

    Overview questions should not rely on keyword search.
    They need broad model slices.
    """

    def __init__(self, graph_repository: GraphRepository):
        self.graph_repository = graph_repository

    def build_context(self, limit_per_type: int = 30) -> str:
        graph = self.graph_repository.get_graph()
        stats = graph.stats()

        actors = graph.find_nodes(node_type=NodeType.ACTOR)[:limit_per_type]
        processes = graph.find_nodes(node_type=NodeType.PROCESS)[:limit_per_type]
        entities = graph.find_nodes(node_type=NodeType.ENTITY)[:limit_per_type]
        facts = graph.find_nodes(node_type=NodeType.FACT)[:limit_per_type]

        lines: list[str] = []
        lines.append("PROJECT OVERVIEW CONTEXT")
        lines.append("")
        lines.append("Graph statistics:")
        for key, value in sorted(stats.items()):
            lines.append(f"- {key}: {value}")

        self._append_nodes(lines, "Actors", actors)
        self._append_nodes(lines, "Processes", processes)
        self._append_nodes(lines, "Entities", entities)
        self._append_nodes(lines, "Facts", facts)

        return "\n".join(lines)

    @staticmethod
    def _append_nodes(lines: list[str], title: str, nodes: list[KnowledgeNode]):
        lines.append("")
        lines.append(f"{title}:")

        if not nodes:
            lines.append("- Not found in graph.")
            return

        for node in nodes:
            description = f" — {node.description}" if node.description else ""
            lines.append(f"- {node.title}{description}")
