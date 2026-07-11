from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from repositories.project_graph_store import project_graph_store


@dataclass(slots=True)
class GraphDiagnosticEvent:
    id: str
    stage: str
    message: str
    project_id: str = "default"
    counts: dict[str, int] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class GraphDiagnostics:
    """
    Runtime diagnostics for the Project Graph pipeline.

    It answers the question:
    where exactly did project knowledge disappear?
    """

    def __init__(self):
        self._events: list[GraphDiagnosticEvent] = []

    def record(
        self,
        stage: str,
        message: str,
        project_id: str = "default",
        counts: dict[str, int] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> GraphDiagnosticEvent:
        graph = project_graph_store.get_graph(project_id)
        graph_stats = graph.stats()

        event = GraphDiagnosticEvent(
            id=str(uuid4()),
            stage=stage,
            message=message,
            project_id=project_id,
            counts={
                **(counts or {}),
                "graph_nodes": graph_stats.get("nodes", 0),
                "graph_edges": graph_stats.get("edges", 0),
                "graph_actors": graph_stats.get("actor", 0),
                "graph_processes": graph_stats.get("process", 0),
                "graph_entities": graph_stats.get("entity", 0),
                "graph_facts": graph_stats.get("fact", 0),
                "graph_sources": graph_stats.get("source", 0),
            },
            metadata=metadata or {},
        )
        self._events.append(event)
        return event

    def list_events(self, project_id: str = "default") -> list[GraphDiagnosticEvent]:
        return [event for event in self._events if event.project_id == project_id]

    def latest_markdown(self, project_id: str = "default", limit: int = 80) -> str:
        events = self.list_events(project_id=project_id)[-limit:]

        lines = ["# Graph Pipeline Diagnostics", ""]

        if not events:
            lines.append("No diagnostic events recorded.")
            return "\n".join(lines)

        for event in events:
            lines.append(f"## {event.created_at.isoformat()} · {event.stage}")
            lines.append(event.message)
            lines.append("")
            lines.append("Counts:")
            for key, value in sorted(event.counts.items()):
                lines.append(f"- {key}: {value}")
            if event.metadata:
                lines.append("Metadata:")
                for key, value in event.metadata.items():
                    lines.append(f"- {key}: {value}")
            lines.append("")

        return "\n".join(lines)


graph_diagnostics = GraphDiagnostics()
