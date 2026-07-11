from __future__ import annotations
from dataclasses import dataclass, field
@dataclass(slots=True)
class QueryPlan:
    intent: str; needs_project_model: bool=True; needs_summary: bool=True; needs_evidence: bool=True; needs_conflicts: bool=False; needs_timeline: bool=False; target_sections: list[str]=field(default_factory=list)
class QueryPlanner:
    def plan(self, question: str) -> QueryPlan:
        q=(question or "").lower()
        if any(t in q for t in ["противореч","conflict","contradict"]): return QueryPlan("conflict_analysis", needs_conflicts=True, target_sections=["business_rules","requirements","decisions"])
        if any(t in q for t in ["измен","changed","change","за неделю","timeline"]): return QueryPlan("change_analysis", needs_timeline=True, target_sections=["decisions","requirements","business_rules"])
        if any(t in q for t in ["интеграц","api","webhook","equifax","bizcap"]): return QueryPlan("integration_question", target_sections=["integrations","entities","business_rules"])
        if any(t in q for t in ["процесс","process","workflow","flow"]): return QueryPlan("process_question", target_sections=["processes","actors","entities","business_rules"])
        if any(t in q for t in ["actor","актор","роль","кто","участник"]): return QueryPlan("actor_question", target_sections=["actors","processes"])
        if any(t in q for t in ["что такое","опиши","расскажи","overview","describe","проект"]): return QueryPlan("project_overview", target_sections=["actors","processes","entities","integrations","business_rules"])
        return QueryPlan("general_question", target_sections=["actors","processes","entities","business_rules","requirements"])
query_planner=QueryPlanner()
