from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class TimelineEvent:
    id: str
    project_id: str
    event_type: str
    title: str
    description: str = ""
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    source_node_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        event_type: str,
        title: str,
        description: str = "",
        project_id: str = "default",
        source_node_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "TimelineEvent":
        return cls(
            id=str(uuid4()),
            project_id=project_id,
            event_type=event_type,
            title=title,
            description=description,
            source_node_id=source_node_id,
            metadata=metadata or {},
        )
