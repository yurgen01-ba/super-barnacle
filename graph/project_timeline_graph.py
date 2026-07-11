from __future__ import annotations

from models.timeline_event import TimelineEvent


class ProjectTimelineGraph:
    """
    Timeline dimension for Project Graph.
    """

    def __init__(self):
        self._events: dict[str, TimelineEvent] = {}

    def add_event(self, event: TimelineEvent) -> TimelineEvent:
        self._events[event.id] = event
        return event

    def add_source_event(
        self,
        title: str,
        description: str = "",
        project_id: str = "default",
        source_node_id: str | None = None,
    ) -> TimelineEvent:
        return self.add_event(
            TimelineEvent.create(
                event_type="source_added",
                title=title,
                description=description,
                project_id=project_id,
                source_node_id=source_node_id,
            )
        )

    def list_events(self, project_id: str = "default") -> list[TimelineEvent]:
        return sorted(
            [event for event in self._events.values() if event.project_id == project_id],
            key=lambda event: event.occurred_at,
        )


project_timeline_graph = ProjectTimelineGraph()
