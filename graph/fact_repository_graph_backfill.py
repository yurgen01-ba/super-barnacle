from __future__ import annotations

from typing import Any

from graph.fact_graph_builder import FactGraphBuilder
from graph.graph_diagnostics import graph_diagnostics
from repositories.project_graph_store import project_graph_store


class FactRepositoryGraphBackfill:
    """
    Backfills Project Graph from persistent canonical facts stored in FactRepository.

    This is the important fix for the current state:
    facts may exist in SQLite `facts`, while Project Graph is empty.
    """

    def __init__(self):
        self.fact_graph_builder = FactGraphBuilder()

    def backfill(self, project_id: str = "default", force: bool = False, limit: int = 5000) -> dict[str, Any]:
        graph = project_graph_store.get_graph(project_id)
        current_stats = graph.stats()

        if current_stats.get("nodes", 0) > 0 and not force:
            return {"status": "skipped", "reason": "graph_not_empty", "stats": current_stats}

        facts = self._load_facts(limit=limit)

        graph_diagnostics.record(
            stage="fact_repository_backfill:loaded_facts",
            message="Loaded canonical facts for Project Graph backfill",
            project_id=project_id,
            counts={"facts_loaded": len(facts)},
        )

        if not facts:
            return {"status": "empty", "reason": "no_facts_found", "stats": current_stats}

        items = [self._fact_to_item(fact) for fact in facts]
        result = self.fact_graph_builder.build_from_items(
            items,
            project_id=project_id,
            source="fact_repository_backfill",
        )

        new_stats = project_graph_store.get_graph(project_id).stats()

        graph_diagnostics.record(
            stage="fact_repository_backfill:completed",
            message="Project Graph backfilled from canonical facts",
            project_id=project_id,
            counts={
                "facts_loaded": len(facts),
                "facts_built": result.facts,
                "actors": result.actors,
                "processes": result.processes,
                "entities": result.entities,
                "edges": result.edges,
                "nodes_after": new_stats.get("nodes", 0),
                "edges_after": new_stats.get("edges", 0),
            },
        )

        return {
            "status": "backfilled",
            "facts_loaded": len(facts),
            "build_result": result,
            "stats": new_stats,
        }

    def _load_facts(self, limit: int) -> list[dict]:
        try:
            from repositories.fact_repository import FactRepository

            repository = FactRepository()
            return repository.list_facts(limit=limit)
        except Exception:
            return []

    def _fact_to_item(self, fact: dict) -> dict[str, Any]:
        subject = str(fact.get("subject") or "").strip()
        predicate = str(fact.get("predicate") or "").strip()
        object_value = str(fact.get("object") or "").strip()
        source = str(fact.get("source") or "fact_repository")

        title = f"{subject} {predicate} {object_value}".strip()

        return {
            "type": "fact",
            "title": title[:240] or f"Fact {fact.get('id')}",
            "content": title,
            "description": title,
            "subject": subject,
            "predicate": predicate,
            "object": object_value,
            "confidence": fact.get("confidence") or 0.7,
            "source": source,
            "source_id": str(fact.get("id") or ""),
            "source_ref": source,
            "metadata": {
                "fact_id": fact.get("id"),
                "fact_type": fact.get("fact_type"),
                "status": fact.get("status"),
                "evidence": fact.get("evidence"),
                "created_at": fact.get("created_at"),
                "updated_at": fact.get("updated_at"),
            },
        }


fact_repository_graph_backfill = FactRepositoryGraphBackfill()
