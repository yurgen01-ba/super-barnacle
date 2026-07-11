from __future__ import annotations
from dataclasses import dataclass
from typing import Any
TYPE_WEIGHTS={"decision":100,"business_rule":95,"requirement":90,"process":80,"integration":75,"data_model":70,"risk":65,"fact":60,"screen_observation":45,"transcript_segment":25,"unknown":10}
@dataclass(slots=True)
class RankedEvidence:
    score: float; fact: dict[str, Any]; reason: str
class EvidenceRankingEngine:
    def rank(self, facts: list[dict[str, Any]], question: str = "", limit: int = 12) -> list[RankedEvidence]:
        terms=[t for t in (question or "").lower().replace('/',' ').replace('-',' ').split() if len(t)>=3]; ranked=[]
        for fact in facts or []:
            score=self._base_score(fact); text=self._text(fact).lower(); matches=sum(1 for t in terms if t in text); score += matches*8
            if fact.get("status") == "confirmed": score += 10
            if fact.get("status") in {"superseded","deprecated","archived"}: score -= 100
            ranked.append(RankedEvidence(score, fact, f"type_weight+confidence+term_match({matches})"))
        ranked.sort(key=lambda x:x.score, reverse=True); return ranked[:limit]
    def _base_score(self, fact): return TYPE_WEIGHTS.get(str(fact.get("fact_type") or fact.get("type") or "unknown"),10) + float(fact.get("confidence") or 0)*20
    @staticmethod
    def _text(f): return " ".join(str(f.get(k) or "") for k in ["subject","predicate","object","title","content","description"])
evidence_ranking_engine=EvidenceRankingEngine()
