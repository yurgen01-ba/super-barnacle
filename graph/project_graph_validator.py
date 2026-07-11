from __future__ import annotations

from dataclasses import dataclass, field

from repositories.project_graph_store import ProjectGraphSnapshot, project_graph_store


@dataclass(slots=True)
class GraphValidationIssue:
    severity: str
    code: str
    message: str
    node_id: str | None = None


@dataclass(slots=True)
class GraphValidationReport:
    issues: list[GraphValidationIssue] = field(default_factory=list)

    def has_errors(self) -> bool:
        return any(issue.severity == "error" for issue in self.issues)

    def to_markdown(self) -> str:
        lines = ["# Project Graph Validation", ""]

        if not self.issues:
            lines.append("No validation issues found.")
            return "\n".join(lines)

        for issue in self.issues:
            node_suffix = f" ({issue.node_id})" if issue.node_id else ""
            lines.append(f"- **{issue.severity.upper()}** `{issue.code}`{node_suffix}: {issue.message}")

        return "\n".join(lines)


class ProjectGraphValidator:
    def validate(self, project_id: str = "default") -> GraphValidationReport:
        graph = project_graph_store.get_graph(project_id)
        return self.validate_snapshot(graph)

    def validate_snapshot(self, graph: ProjectGraphSnapshot) -> GraphValidationReport:
        issues: list[GraphValidationIssue] = []
        connected = set()

        for edge in graph.edges:
            if edge.from_node_id not in graph.nodes:
                issues.append(GraphValidationIssue("error", "missing_from_node", "Edge points from missing node", edge.from_node_id))
            if edge.to_node_id not in graph.nodes:
                issues.append(GraphValidationIssue("error", "missing_to_node", "Edge points to missing node", edge.to_node_id))
            connected.add(edge.from_node_id)
            connected.add(edge.to_node_id)

        for node in graph.nodes.values():
            if not node.title.strip():
                issues.append(GraphValidationIssue("error", "empty_title", "Node has empty title", node.id))

            if not node.description.strip():
                issues.append(GraphValidationIssue("warning", "missing_description", "Node has no description", node.id))

            if node.node_type != "source" and not node.source:
                issues.append(GraphValidationIssue("warning", "missing_source", "Knowledge node has no source", node.id))

            if node.id not in connected and node.node_type != "source":
                issues.append(GraphValidationIssue("info", "orphan_node", "Node is not connected to other nodes", node.id))

        return GraphValidationReport(issues=issues)
