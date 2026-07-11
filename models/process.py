from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProcessProfile:
    name: str
    description: str | None = None
    process_type: str = "business_process"
    goal: str | None = None
    participants: list[dict[str, Any]] = field(default_factory=list)
    business_objects: list[dict[str, Any]] = field(default_factory=list)
    steps: list[dict[str, Any]] = field(default_factory=list)
    inputs: list[dict[str, Any]] = field(default_factory=list)
    outputs: list[dict[str, Any]] = field(default_factory=list)
    rules: list[dict[str, Any]] = field(default_factory=list)
    exceptions: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.7

