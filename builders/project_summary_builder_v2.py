from __future__ import annotations

from collections import Counter

from models.project_summary import ProjectSummary
from repositories.project_graph_store import project_graph_store
from repositories.project_summary_repository import project_summary_repository


class ProjectSummaryBuilderV2:
    """
    Builds structured project summary from canonical Project Graph.
    """

    DEFAULT_DOMAIN = "Merchant Cash Advance / credit operations"

    DEFAULT_DESCRIPTION = (
        "OrgMeter is a platform for managing MCA-style credits / Advances, "
        "merchants, funders, partners, underwriting, payback allocation, fees, "
        "payout history, reporting and external integrations."
    )

    def build_and_save(self, project_id: str = "default") -> ProjectSummary:
        graph = project_graph_store.get_graph(project_id, hydrate=False)

        actors = self._titles_by_type("actor", project_id)
        processes = self._titles_by_type("process", project_id)
        entities = self._titles_by_type("entity", project_id)
        integrations = self._titles_by_type("integration", project_id)
        facts = self._titles_by_type("fact", project_id, limit=40)

        business_rules = [
            fact for fact in facts
            if any(term in fact.lower() for term in ["fee", "payback", "allocation", "status", "rule", "advance"])
        ][:20]

        summary = ProjectSummary(
            project_id=project_id,
            domain=self.DEFAULT_DOMAIN,
            description=self.DEFAULT_DESCRIPTION,
            actors=actors,
            processes=processes,
            entities=entities,
            business_rules=business_rules,
            integrations=integrations,
            open_questions=self._derive_open_questions(actors, processes, entities),
            metadata={
                "graph_stats": graph.stats(),
                "builder": "ProjectSummaryBuilderV2",
            },
        )

        return project_summary_repository.save(summary)

    def _titles_by_type(self, node_type: str, project_id: str, limit: int = 100) -> list[str]:
        graph = project_graph_store.get_graph(project_id, hydrate=False)
        nodes = [
            node for node in graph.nodes.values()
            if node.node_type == node_type and node.metadata.get("project_id", project_id) == project_id
        ]
        counter = Counter(node.title for node in nodes if node.title)
        return [title for title, _ in counter.most_common(limit)]

    def _derive_open_questions(self, actors: list[str], processes: list[str], entities: list[str]) -> list[str]:
        questions = []

        if not actors:
            questions.append("Actors are not confidently extracted yet.")
        if not processes:
            questions.append("Processes are not confidently extracted yet.")
        if not entities:
            questions.append("Entities are not confidently extracted yet.")

        return questions


project_summary_builder_v2 = ProjectSummaryBuilderV2()
