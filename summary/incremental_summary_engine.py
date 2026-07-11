from __future__ import annotations
from datetime import datetime
from domain.domain_dictionary import domain_dictionary
from models.project_model import ProjectModelItem
from repositories.project_model_repository import project_model_repository

class IncrementalSummaryEngine:
    def update_from_facts(self, facts: list[dict], project_id: str = "default"):
        model=project_model_repository.get_or_create(project_id)
        for fact in facts or []:
            text=self._fact_text(fact)
            for term in domain_dictionary.resolve_text(text):
                item=ProjectModelItem.create(item_type=term.term_type, canonical_name=term.canonical, display_name=term.ru_label, description=term.description, confidence=float(fact.get("confidence") or 0.7), source_ids=[str(fact.get("source") or "")], evidence_ids=[str(fact.get("source_id") or fact.get("id") or "")], metadata={"source_fact": fact})
                self._upsert_item(model, item)
            if self._is_business_rule(fact):
                rule=ProjectModelItem.create(item_type="business_rule", canonical_name=str(fact.get("subject") or "Business Rule"), display_name=str(fact.get("subject") or "Business Rule"), description=text, confidence=float(fact.get("confidence") or 0.7), source_ids=[str(fact.get("source") or "")], evidence_ids=[str(fact.get("source_id") or fact.get("id") or "")], metadata={"source_fact": fact})
                self._upsert_item(model, rule)
        model.version += 1; model.updated_at=datetime.utcnow(); return project_model_repository.save(model)
    def _upsert_item(self, model, item):
        coll=getattr(model, self._collection_for_item_type(item.item_type))
        for e in coll:
            if e.canonical_name == item.canonical_name:
                e.confidence=max(e.confidence, item.confidence); e.source_ids=sorted(set(e.source_ids+item.source_ids)); e.evidence_ids=sorted(set(e.evidence_ids+item.evidence_ids)); e.description=e.description or item.description; return
        coll.append(item)
    @staticmethod
    def _collection_for_item_type(t): return {"actor":"actors","process":"processes","entity":"entities","integration":"integrations","business_rule":"business_rules","requirement":"requirements","decision":"decisions","risk":"risks","question":"open_questions"}.get(t,"entities")
    @staticmethod
    def _fact_text(f): return " ".join(str(f.get(k) or "") for k in ["subject","predicate","object","title","content","description"])
    @staticmethod
    def _is_business_rule(f):
        ft=str(f.get("fact_type") or f.get("type") or "").lower(); text=IncrementalSummaryEngine._fact_text(f).lower()
        return ft == "business_rule" or any(x in text for x in ["must","should","fee","rule","status","payback","allocation"])
incremental_summary_engine=IncrementalSummaryEngine()
