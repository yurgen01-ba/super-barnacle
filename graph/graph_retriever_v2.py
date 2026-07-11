from __future__ import annotations

from dataclasses import dataclass, field

from graph.evidence_retriever import evidence_retriever
from graph.graph_intent import GraphIntent, detect_graph_intent
from graph.project_graph_hydration import project_graph_hydration_service
from repositories.project_graph_store import project_graph_store
from repositories.project_summary_repository import project_summary_repository


@dataclass(slots=True)
class GraphRetrieverResponse:
    intent: str
    context: str
    stats: dict[str, int] = field(default_factory=dict)


class GraphRetrieverV2:
    """
    Evidence-based retriever.

    Retrieval order:
    1. Structured Project Summary
    2. Relevant evidence facts
    3. Graph stats
    """

    def __init__(self, project_id: str = "default"):
        self.project_id = project_id

    def retrieve(self, question: str, refresh: bool = True) -> GraphRetrieverResponse:
        if refresh:
            project_graph_hydration_service.hydrate(self.project_id, backfill_if_empty=True)

        intent = detect_graph_intent(question)
        graph = project_graph_store.get_graph(self.project_id, hydrate=False)
        stats = graph.stats()

        summary = self._get_or_build_summary()
        evidence = evidence_retriever.retrieve_evidence(question, project_id=self.project_id)

        context = self._build_context(summary=summary, evidence=evidence, stats=stats)

        return GraphRetrieverResponse(intent=intent, context=context, stats=stats)

    def _get_or_build_summary(self) -> dict:
        summary = project_summary_repository.get(self.project_id)
        if summary:
            return summary

        try:
            from builders.project_summary_builder_v2 import project_summary_builder_v2

            return project_summary_builder_v2.build_and_save(self.project_id).to_dict()
        except Exception:
            return {
                "project_id": self.project_id,
                "domain": "Merchant Cash Advance / credit operations",
                "description": "OrgMeter is a platform for managing MCA-style credits / Advances and related operations.",
                "actors": [],
                "processes": [],
                "entities": [],
                "business_rules": [],
                "integrations": [],
                "open_questions": ["Project Summary could not be built yet."],
            }

    def _build_context(self, summary: dict, evidence: list[str], stats: dict[str, int]) -> str:
        lines = []
        lines.append("PROJECT SUMMARY")
        lines.append(f"Domain: {summary.get('domain')}")
        lines.append(f"Description: {summary.get('description')}")
        lines.append("")

        self._append_list(lines, "Actors", summary.get("actors") or [])
        self._append_list(lines, "Processes", summary.get("processes") or [])
        self._append_list(lines, "Entities", summary.get("entities") or [])
        self._append_list(lines, "Business rules", summary.get("business_rules") or [])
        self._append_list(lines, "Integrations", summary.get("integrations") or [])
        self._append_list(lines, "Open questions", summary.get("open_questions") or [])

        lines.append("")
        lines.append("RELEVANT EVIDENCE")
        if evidence:
            for item in evidence:
                lines.append(f"- {item}")
        else:
            lines.append("- No specific supporting facts found for this question.")

        lines.append("")
        lines.append("GRAPH STATS")
        for key, value in sorted(stats.items()):
            lines.append(f"- {key}: {value}")

        return "\n".join(lines)

    @staticmethod
    def _append_list(lines: list[str], title: str, values: list[str]):
        lines.append("")
        lines.append(title + ":")
        if not values:
            lines.append("- Not confidently extracted yet.")
            return
        for value in values[:30]:
            lines.append(f"- {value}")
