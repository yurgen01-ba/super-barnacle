from dataclasses import dataclass
from typing import Any


FACT_TYPES = [
    "business_rule",
    "requirement",
    "decision",
    "risk",
    "question",
    "assumption",
    "integration",
    "glossary",
    "action_item",
    "api",
    "ui_screen",
    "data_model",
    "process",
    "constraint",
    "dependency",
    "bug",
    "role",
    "status",
    "workflow",
    "unknown",
]


FACT_STATUSES = [
    "proposed",
    "confirmed",
    "superseded",
    "deprecated",
]


@dataclass
class CanonicalFact:
    subject: str
    predicate: str
    object: str
    fact_type: str = "unknown"
    confidence: float = 0.7
    status: str = "proposed"
    evidence: str | None = None
    source: str | None = None
    metadata: dict[str, Any] | None = None

    def normalized(self) -> dict:
        fact_type = self.fact_type if self.fact_type in FACT_TYPES else "unknown"
        status = self.status if self.status in FACT_STATUSES else "proposed"

        confidence = self.confidence
        try:
            confidence = float(confidence)
        except Exception:
            confidence = 0.7

        confidence = max(0.0, min(confidence, 1.0))

        return {
            "subject": (self.subject or "").strip()[:240],
            "predicate": (self.predicate or "").strip()[:160],
            "object": (self.object or "").strip()[:1200],
            "fact_type": fact_type,
            "confidence": confidence,
            "status": status,
            "evidence": self.evidence,
            "source": self.source,
            "metadata": self.metadata or {},
        }

