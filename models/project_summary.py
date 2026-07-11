from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class ProjectSummary:
    project_id: str
    domain: str
    description: str
    actors: list[str] = field(default_factory=list)
    processes: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    business_rules: list[str] = field(default_factory=list)
    integrations: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "domain": self.domain,
            "description": self.description,
            "actors": self.actors,
            "processes": self.processes,
            "entities": self.entities,
            "business_rules": self.business_rules,
            "integrations": self.integrations,
            "open_questions": self.open_questions,
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }
