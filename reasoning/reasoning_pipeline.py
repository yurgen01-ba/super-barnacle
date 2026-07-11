from __future__ import annotations
from knowledge.conflict_detection import conflict_detection_engine
from repositories.project_model_repository import project_model_repository
from retrieval.evidence_ranking import evidence_ranking_engine
from retrieval.query_planner import query_planner
class ReasoningPipeline:
    def build_context(self, question: str, project_id: str = "default", facts: list[dict] | None = None) -> dict:
        plan=query_planner.plan(question); model=project_model_repository.get_or_create(project_id); facts=facts or self._load_facts(); ranked=evidence_ranking_engine.rank(facts, question, 12) if plan.needs_evidence else []; conflicts=conflict_detection_engine.detect(facts) if plan.needs_conflicts else []
        return {"plan":plan,"project_model":model,"ranked_evidence":ranked,"conflicts":conflicts,"prompt_context":self._format(model, plan, ranked, conflicts)}
    def _load_facts(self):
        try:
            from repositories.fact_repository import FactRepository
            return FactRepository().list_facts(limit=5000)
        except Exception: return []
    def _format(self, model, plan, ranked, conflicts):
        lines=["PROJECT MODEL",f"Domain: {model.domain}",f"Description: {model.description}",f"Version: {model.version}","",f"QUERY PLAN: {plan.intent}",f"Target sections: {', '.join(plan.target_sections)}"]
        for title, items in [("Actors",model.actors),("Processes",model.processes),("Entities",model.entities),("Integrations",model.integrations),("Business Rules",model.business_rules),("Requirements",model.requirements),("Decisions",model.decisions),("Risks",model.risks),("Open Questions",model.open_questions)]: self._append(lines,title,items)
        lines += ["","RANKED EVIDENCE"]
        if not ranked: lines.append("- No ranked evidence found.")
        for item in ranked:
            f=item.fact; text=" ".join(str(f.get(k) or "") for k in ["subject","predicate","object","content","description"]); lines.append(f"- score={round(item.score,2)} reason={item.reason}: {text[:600]}")
        lines += ["","CONFLICTS"]
        if not conflicts: lines.append("- No conflicts detected for this query.")
        for c in conflicts[:10]: lines.append(f"- {c.subject} / {c.predicate}: {c.reason}")
        return "\n".join(lines)
    @staticmethod
    def _append(lines, title, items):
        lines += ["", title+":"]
        if not items: lines.append("- Not confidently extracted yet."); return
        for item in items[:30]: lines.append(f"- {item.display_name}: {item.description}")
reasoning_pipeline=ReasoningPipeline()
