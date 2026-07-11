from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from domain.domain_dictionary import domain_dictionary
from ontology.ontology_resolver import ontology_resolver


@dataclass(slots=True)
class ConfidenceDecision:
    accepted: bool
    confidence: float
    reason: str


class ConfidenceGate:
    """
    Drops low-confidence or ontology-unknown facts before graph ingestion.
    """

    def __init__(self, min_confidence: float = 0.62):
        self.min_confidence = min_confidence

    def evaluate(self, fact: dict[str, Any]) -> ConfidenceDecision:
        try:
            confidence = float(fact.get("confidence") or 0.0)
        except Exception:
            confidence = 0.0

        if confidence < self.min_confidence:
            return ConfidenceDecision(False, confidence, "confidence_below_threshold")

        resolved = ontology_resolver.resolve_fact(fact)
        if not resolved:
            return ConfidenceDecision(False, confidence, "no_known_ontology_terms")

        return ConfidenceDecision(True, confidence, "accepted")

    def filter(self, facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        accepted = []

        for fact in facts or []:
            if not isinstance(fact, dict):
                continue

            decision = self.evaluate(fact)
            if not decision.accepted:
                continue

            accepted.append(fact)

        return accepted


confidence_gate = ConfidenceGate()
