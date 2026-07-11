from __future__ import annotations

from dataclasses import dataclass, field

from graph.project_graph_validator import GraphValidationIssue, ProjectGraphValidator
from repositories.project_graph_store import project_graph_store


@dataclass(slots=True)
class KnowledgeIntegrityReport:
    issues: list[GraphValidationIssue] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = ["# Knowledge Integrity Report", ""]

        if not self.issues:
            lines.append("No integrity issues found.")
            return "\n".join(lines)

        for issue in self.issues:
            node_suffix = f" ({issue.node_id})" if issue.node_id else ""
            lines.append(f"- **{issue.severity.upper()}** `{issue.code}`{node_suffix}: {issue.message}")

        return "\n".join(lines)


class KnowledgeIntegrityChecker:
    """
    First automated quality checker for Project Graph.

    Checks:
    - validation issues;
    - duplicate titles by node type;
    - source coverage;
    - orphan processes/entities/facts.
    """

    def __init__(self):
        self.validator = ProjectGraphValidator()

    def inspect(self, project_id: str = "default") -> KnowledgeIntegrityReport:
        graph = project_graph_store.get_graph(project_id)
        validation = self.validator.validate_snapshot(graph)
        issues = list(validation.issues)

        issues.extend(self._find_duplicate_titles(graph))
        issues.extend(self._find_facts_without_sources(graph))

        return KnowledgeIntegrityReport(issues=issues)

    def _find_duplicate_titles(self, graph) -> list[GraphValidationIssue]:
        seen: dict[tuple[str, str], str] = {}
        issues: list[GraphValidationIssue] = []

        for node in graph.nodes.values():
            key = (node.node_type, node.title.strip().lower())
            if key in seen:
                issues.append(
                    GraphValidationIssue(
                        severity="warning",
                        code="duplicate_node_title",
                        message=f"Duplicate {node.node_type} title: {node.title}",
                        node_id=node.id,
                    )
                )
            else:
                seen[key] = node.id

        return issues

    def _find_facts_without_sources(self, graph) -> list[GraphValidationIssue]:
        return [
            GraphValidationIssue(
                severity="warning",
                code="fact_without_source",
                message="Fact has no source reference",
                node_id=node.id,
            )
            for node in graph.nodes.values()
            if node.node_type == "fact" and not node.source
        ]
