from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Evidence:
    """
    Evidence explains why a node or edge exists.

    For now this is a lightweight model used by the graph layer.
    Later it can be persisted and linked to source chunks, timestamps,
    Jira issues, Confluence pages and meeting frames.
    """

    id: str
    source_type: str
    source_id: str | None = None
    source_ref: str = ""
    quote: str = ""
    confidence: float = 0.7
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source_type": self.source_type,
            "source_id": self.source_id,
            "source_ref": self.source_ref,
            "quote": self.quote,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }
