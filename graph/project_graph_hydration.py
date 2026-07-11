from __future__ import annotations

from repositories.project_graph_store import project_graph_store


class ProjectGraphHydrationService:
    """
    Hydrates Project Graph and guarantees best-effort backfill before chat retrieval.
    """

    def hydrate(self, project_id: str = "default", backfill_if_empty: bool = True) -> dict[str, int]:
        hydrate_method = getattr(project_graph_store, "hydrate", None)

        if callable(hydrate_method):
            hydrate_method(project_id)
            stats = project_graph_store.get_graph(project_id, hydrate=False).stats()
        else:
            stats = project_graph_store.get_graph(project_id).stats()

        if backfill_if_empty and stats.get("nodes", 0) == 0:
            self._backfill_from_facts(project_id)
            stats = project_graph_store.get_graph(project_id, hydrate=False).stats()

        if backfill_if_empty and stats.get("nodes", 0) == 0:
            self._backfill_from_memory(project_id)
            stats = project_graph_store.get_graph(project_id, hydrate=False).stats()

        return stats

    def _backfill_from_facts(self, project_id: str):
        try:
            from graph.fact_repository_graph_backfill import fact_repository_graph_backfill
            fact_repository_graph_backfill.backfill(project_id=project_id, force=False)
        except Exception:
            pass

    def _backfill_from_memory(self, project_id: str):
        try:
            from graph.memory_graph_backfill import memory_graph_backfill
            memory_graph_backfill.backfill(project_id=project_id, force=False)
        except Exception:
            pass

    def persisted_stats(self, project_id: str = "default") -> dict[str, int]:
        try:
            from repositories.persistent_project_graph_repository import persistent_project_graph_repository
            return persistent_project_graph_repository.stats(project_id)
        except Exception:
            return {"nodes": 0, "edges": 0}


project_graph_hydration_service = ProjectGraphHydrationService()
