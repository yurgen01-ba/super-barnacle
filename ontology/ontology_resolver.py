from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from domain.domain_dictionary import DomainTerm, domain_dictionary


@dataclass(slots=True)
class ResolvedOntologyItem:
    canonical: str
    node_type: str
    ru_label: str
    en_label: str
    confidence: float
    source_text: str
    metadata: dict[str, Any] = field(default_factory=dict)


class OntologyResolver:
    """
    Resolves extracted facts to canonical OrgMeter ontology nodes.

    This replaces "create node if word matched" behavior.
    Unknown terms do not become actors/processes/entities automatically.
    """

    def resolve_fact(self, fact: dict[str, Any]) -> list[ResolvedOntologyItem]:
        text = self._fact_text(fact)
        terms = domain_dictionary.resolve_text(text)

        resolved = []

        for term in terms:
            confidence = self._confidence_for_term(term, fact, text)
            resolved.append(
                ResolvedOntologyItem(
                    canonical=term.canonical,
                    node_type=self._node_type(term),
                    ru_label=term.ru_label,
                    en_label=term.en_label,
                    confidence=confidence,
                    source_text=text,
                    metadata={
                        "term_description": term.description,
                        "raw_fact": fact,
                    },
                )
            )

        return resolved

    def normalize_fact(self, fact: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(fact or {})
        text = self._fact_text(normalized)

        for term in domain_dictionary.resolve_text(text):
            for key in ["subject", "object", "title", "content", "description", "text"]:
                if key in normalized and normalized[key]:
                    value = str(normalized[key])
                    for alias in term.aliases:
                        value = self._replace_alias(value, alias, term.canonical)
                    normalized[key] = value

        return normalized

    def _confidence_for_term(self, term: DomainTerm, fact: dict[str, Any], text: str) -> float:
        base = float(fact.get("confidence") or 0.7)
        text_l = text.lower()

        if term.canonical.lower() in text_l:
            return min(1.0, base + 0.15)

        if any(alias.lower() in text_l for alias in term.aliases):
            return min(1.0, base + 0.05)

        return base

    @staticmethod
    def _node_type(term: DomainTerm) -> str:
        if term.term_type in {"actor", "process", "entity", "integration"}:
            return term.term_type
        return "entity"

    @staticmethod
    def _fact_text(fact: dict[str, Any]) -> str:
        return " ".join(
            str(fact.get(key) or "")
            for key in ["subject", "predicate", "object", "title", "content", "description", "text"]
        ).strip()

    @staticmethod
    def _replace_alias(value: str, alias: str, canonical: str) -> str:
        import re

        return re.sub(
            rf"\b{re.escape(alias)}\b",
            canonical,
            value,
            flags=re.IGNORECASE,
        )


ontology_resolver = OntologyResolver()
