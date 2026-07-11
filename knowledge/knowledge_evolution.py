from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(slots=True)
class EvolutionDecision:
    action: str
    reason: str
    previous_id: str | None = None

class KnowledgeEvolutionEngine:
    def decide(self, new_fact: dict[str, Any], existing_facts: list[dict[str, Any]]) -> EvolutionDecision:
        ns, np, no = self._norm(new_fact.get("subject")), self._norm(new_fact.get("predicate")), self._norm(new_fact.get("object"))
        for existing in existing_facts or []:
            if self._norm(existing.get("subject")) == ns and self._norm(existing.get("predicate")) == np:
                if self._norm(existing.get("object")) == no:
                    return EvolutionDecision("confirm_existing", "same_subject_predicate_object", str(existing.get("id") or ""))
                return EvolutionDecision("supersede_existing", "same_subject_predicate_different_object", str(existing.get("id") or ""))
        return EvolutionDecision("create_new", "no_matching_fact")
    def apply(self, new_fact: dict[str, Any], existing_facts: list[dict[str, Any]]) -> dict[str, Any]:
        d=self.decide(new_fact, existing_facts); r=dict(new_fact); r["evolution_action"]=d.action; r["evolution_reason"]=d.reason
        if d.previous_id: r["supersedes"]=d.previous_id
        return r
    @staticmethod
    def _norm(v): return str(v or "").strip().lower()
knowledge_evolution_engine=KnowledgeEvolutionEngine()
