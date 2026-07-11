from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

@dataclass(slots=True)
class Extraction:
    id: str
    project_id: str
    source_id: str
    source_name: str
    source_type: str
    status: str = "created"
    started_at: datetime = field(default_factory=datetime.utcnow)
    finished_at: datetime | None = None
    duration_seconds: float | None = None
    artifact_count: int = 0
    statistics: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, source_id: str, source_name: str, source_type: str, project_id: str = "default") -> "Extraction":
        return cls(id=str(uuid4()), project_id=project_id, source_id=source_id, source_name=source_name, source_type=source_type)

    def complete(self, artifact_count: int = 0, statistics: dict[str, Any] | None = None):
        self.status = "completed"
        self.finished_at = datetime.utcnow()
        self.duration_seconds = (self.finished_at - self.started_at).total_seconds()
        self.artifact_count = artifact_count
        self.statistics = statistics or self.statistics

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "project_id": self.project_id, "source_id": self.source_id,
            "source_name": self.source_name, "source_type": self.source_type,
            "status": self.status, "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "duration_seconds": self.duration_seconds, "artifact_count": self.artifact_count,
            "statistics": self.statistics, "metadata": self.metadata,
        }
