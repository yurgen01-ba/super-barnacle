from __future__ import annotations

from dataclasses import dataclass, field

from graph.graph_repository import GraphRepository


@dataclass(slots=True)
class GraphHealthReport:
    stats: dict[str, int]
    orphan_nodes: list[str] = field(default_factory=list)
    missing_descriptions: list[str] = field(default_factory=list)
    low_confidence_nodes: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines: list[str] = ["# Graph Health", ""]

        lines.append("## Stats")
        for key, value in sorted(self.stats.items()):
            lines.append(f"- {key}: {value}")

        lines.append("")
        lines.append("## Orphan nodes")
        lines.extend([f"- {item}" for item in self.orphan_nodes] or ["- None"])

        lines.append("")
        lines.append("## Missing descriptions")
        lines.extend([f"- {item}" for item in self.missing_descriptions] or ["- None"])

        lines.append("")
        lines.append("## Low confidence nodes")
        lines.extend([f"- {item}" for item in self.low_confidence_nodes] or ["- None"])

        return "\n".join(lines)


class GraphHealthService:
    def __init__(self, graph_repository: GraphRepository):
        self.graph_repository = graph_repository

    def inspect(self, refresh: bool = False) -> GraphHealthReport:
        graph = self.graph_repository.get_graph(refresh=refresh)
        connected = set()

        for edge in graph.edges:
            connected.add(edge.from_node_id)
            connected.add(edge.to_node_id)

        orphan_nodes = [
            f"{node.id} | {node.title}"
            for node in graph.nodes.values()
            if node.id not in connected
        ]

        missing_descriptions = [
            f"{node.id} | {node.title}"
            for node in graph.nodes.values()
            if not node.description
        ]

        low_confidence_nodes = [
            f"{node.id} | {node.title} | confidence={node.confidence}"
            for node in graph.nodes.values()
            if float(node.confidence or 0) < 0.5
        ]

        return GraphHealthReport(
            stats=graph.stats(),
            orphan_nodes=orphan_nodes,
            missing_descriptions=missing_descriptions,
            low_confidence_nodes=low_confidence_nodes,
        )
