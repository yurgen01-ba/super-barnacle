from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class KnowledgeEdge:
    """
    Relationship between two KnowledgeNodes.

    This is a graph read-model edge. Persistence can be added later.
    """

    id: str
    from_node_id: str
    to_node_id: str
    relationship_type: str
    confidence: float = 0.7
    source: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "from_node_id": self.from_node_id,
            "to_node_id": self.to_node_id,
            "relationship_type": self.relationship_type,
            "confidence": self.confidence,
            "source": self.source,
            "metadata": self.metadata,
        }
