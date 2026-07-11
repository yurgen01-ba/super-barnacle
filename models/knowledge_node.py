from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class KnowledgeNode:
    """
    Universal read-model object for Project Brain Knowledge Graph.

    This is intentionally a lightweight adapter model.
    It does not replace existing Facts, Actors, Processes or Entities yet.
    """

    id: str
    node_type: str
    title: str
    description: str = ""
    confidence: float = 0.7
    status: str = "active"
    source: str = ""
    source_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "node_type": self.node_type,
            "title": self.title,
            "description": self.description,
            "confidence": self.confidence,
            "status": self.status,
            "source": self.source,
            "source_id": self.source_id,
            "metadata": self.metadata,
        }
