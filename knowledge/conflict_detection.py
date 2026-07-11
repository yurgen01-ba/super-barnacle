from __future__ import annotations
from dataclasses import dataclass
from typing import Any
NEGATION_MARKERS={"cannot","can't","must not","should not","not allowed","нельзя","не может","запрещено","не должен"}
@dataclass(slots=True)
class KnowledgeConflict:
    subject: str; predicate: str; fact_a: dict[str, Any]; fact_b: dict[str, Any]; reason: str
class ConflictDetectionEngine:
    def detect(self, facts: list[dict[str, Any]]) -> list[KnowledgeConflict]:
        conflicts=[]; grouped={}
        for fact in facts or []:
            key=(self._norm(fact.get("subject")), self._norm(fact.get("predicate")))
            if key[0] and key[1]: grouped.setdefault(key, []).append(fact)
        for (s,p), group in grouped.items():
            for i,a in enumerate(group):
                for b in group[i+1:]:
                    if self._conflict(a,b): conflicts.append(KnowledgeConflict(s,p,a,b,"same_subject_predicate_conflicting_objects_or_negation"))
        return conflicts
    def _conflict(self,a,b):
        oa,ob=self._norm(a.get("object")),self._norm(b.get("object"))
        if oa and ob and oa != ob: return True
        return self._has_negation(self._text(a)) != self._has_negation(self._text(b))
    @staticmethod
    def _has_negation(t):
        tl=t.lower(); return any(m in tl for m in NEGATION_MARKERS)
    @staticmethod
    def _text(f): return " ".join(str(f.get(k) or "") for k in ["subject","predicate","object","content","description"])
    @staticmethod
    def _norm(v): return str(v or "").strip().lower()
conflict_detection_engine=ConflictDetectionEngine()
