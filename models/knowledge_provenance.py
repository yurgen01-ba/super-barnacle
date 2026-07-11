from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4
@dataclass(slots=True)
class ProvenanceRecord:
    id: str; project_id: str; source_id: str; source_type: str; artifact_type: str; title: str; content: str; stage: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)
    @classmethod
    def create(cls, source_id, source_type, artifact_type, title, content, stage, project_id='default', metadata=None):
        return cls(str(uuid4()), project_id, source_id, source_type, artifact_type, title, content or '', stage, metadata=metadata or {})
