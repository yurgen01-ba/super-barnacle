from __future__ import annotations

from models.knowledge_node import KnowledgeNode
from repositories.project_graph_store import project_graph_store


class ProjectGraphOverview:
    """
    Builds overview context directly from ProjectGraphStore.

    This avoids old empty repositories and makes project overview answers use
    real graph nodes: actors, processes, entities, facts and relationships.
    """

    def build_context(self, project_id: str = "default", limit_per_type: int = 40) -> str:
        graph = project_graph_store.get_graph(project_id)

        actors = self._nodes_by_type("actor", project_id)[:limit_per_type]
        processes = self._nodes_by_type("process", project_id)[:limit_per_type]
        entities = self._nodes_by_type("entity", project_id)[:limit_per_type]
        facts = self._nodes_by_type("fact", project_id)[:limit_per_type]
        sources = self._nodes_by_type("source", project_id)[:limit_per_type]

        lines = []
        lines.append("PROJECT GRAPH OVERVIEW CONTEXT")
        lines.append("")
        lines.append("Graph statistics:")
        for key, value in sorted(graph.stats().items()):
            lines.append(f"- {key}: {value}")

        self._append_nodes(lines, "Actors", actors)
        self._append_nodes(lines, "Processes", processes)
        self._append_nodes(lines, "Entities", entities)
        self._append_nodes(lines, "Facts", facts)
        self._append_nodes(lines, "Sources", sources)

        lines.append("")
        lines.append("Relationships:")
        if not graph.edges:
            lines.append("- No relationships found.")
        else:
            for edge in graph.edges[:80]:
                from_node = graph.nodes.get(edge.from_node_id)
                to_node = graph.nodes.get(edge.to_node_id)
                if from_node and to_node:
                    lines.append(f"- [{from_node.node_type}] {from_node.title} --{edge.relationship_type}--> [{to_node.node_type}] {to_node.title}")

        return "\n".join(lines)

    def _nodes_by_type(self, node_type: str, project_id: str) -> list[KnowledgeNode]:
        graph = project_graph_store.get_graph(project_id)
        return sorted(
            [
                node for node in graph.nodes.values()
                if node.node_type == node_type and node.metadata.get("project_id", project_id) == project_id
            ],
            key=lambda node: node.title.lower(),
        )

    @staticmethod
    def _append_nodes(lines: list[str], title: str, nodes: list[KnowledgeNode]):
        lines.append("")
        lines.append(f"{title}:")

        if not nodes:
            lines.append("- Not found.")
            return

        for node in nodes:
            description = f" — {node.description[:220]}" if node.description else ""
            lines.append(f"- {node.title}{description}")
