from dataclasses import dataclass, field
from typing import Any


@dataclass
class ActorProfile:
    entity_id: int
    name: str
    actor_type: str = "unknown"
    description: str | None = None
    responsibilities: list[dict[str, Any]] = field(default_factory=list)
    owned_objects: list[dict[str, Any]] = field(default_factory=list)
    participates_in: list[dict[str, Any]] = field(default_factory=list)
    interactions: list[dict[str, Any]] = field(default_factory=list)
    permissions: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.7

