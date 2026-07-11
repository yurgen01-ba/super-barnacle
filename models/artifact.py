from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

@dataclass(slots=True)
class KnowledgeArtifact:
    id: str
    extraction_id: str
    project_id: str
    artifact_type: str
    title: str
    description: str
    content: str
    format: str = "text"
    status: str = "ready"
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, extraction_id: str, project_id: str, artifact_type: str, title: str, content: str, description: str = "", format: str = "text", metadata: dict[str, Any] | None = None):
        return cls(id=str(uuid4()), extraction_id=extraction_id, project_id=project_id, artifact_type=artifact_type, title=title, description=description, content=content or "", format=format, metadata=metadata or {})

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "extraction_id": self.extraction_id, "project_id": self.project_id,
            "artifact_type": self.artifact_type, "title": self.title, "description": self.description,
            "content": self.content, "format": self.format, "status": self.status,
            "created_at": self.created_at.isoformat(), "metadata": self.metadata,
        }
