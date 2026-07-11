from __future__ import annotations

from typing import Any

from graph.fact_graph_builder import FactGraphBuilder
from graph.graph_diagnostics import graph_diagnostics
from repositories.project_graph_store import project_graph_store


class MemoryGraphBackfill:
    """
    Builds Project Graph from already saved Project Memory items.

    This fixes the practical situation where memory/facts exist, but the new
    ProjectGraphStore is empty because graph persistence was introduced later.
    """

    def __init__(self):
        self.fact_graph_builder = FactGraphBuilder()

    def backfill(self, project_id: str = "default", force: bool = False) -> dict[str, Any]:
        graph = project_graph_store.get_graph(project_id)
        current_stats = graph.stats()

        if current_stats.get("nodes", 0) > 0 and not force:
            return {
                "status": "skipped",
                "reason": "graph_not_empty",
                "stats": current_stats,
            }

        items = self._load_memory_items()

        graph_diagnostics.record(
            stage="memory_graph_backfill:loaded_memory",
            message="Loaded memory items for Project Graph backfill",
            project_id=project_id,
            counts={"memory_items": len(items)},
        )

        if not items:
            return {
                "status": "empty",
                "reason": "no_memory_items_found",
                "stats": current_stats,
            }

        normalized_items = [self._normalize_item(item) for item in items]
        normalized_items = [item for item in normalized_items if item]

        result = self.fact_graph_builder.build_from_items(
            normalized_items,
            project_id=project_id,
            source="memory_graph_backfill",
        )

        new_stats = project_graph_store.get_graph(project_id).stats()

        graph_diagnostics.record(
            stage="memory_graph_backfill:completed",
            message="Project Graph backfilled from memory",
            project_id=project_id,
            counts={
                "memory_items": len(items),
                "normalized_items": len(normalized_items),
                "facts": result.facts,
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
            "memory_items": len(items),
            "normalized_items": len(normalized_items),
            "build_result": result,
            "stats": new_stats,
        }

    def _load_memory_items(self) -> list[Any]:
        try:
            from repositories.memory_repository import MemoryRepository
        except Exception:
            return []

        try:
            repository = MemoryRepository()
        except Exception:
            return []

        method_names = [
            "list_items",
            "list_memory_items",
            "get_items",
            "get_all_items",
            "get_all",
            "list_all",
            "list",
            "all",
            "load",
            "load_all",
        ]

        for method_name in method_names:
            method = getattr(repository, method_name, None)
            if not callable(method):
                continue

            try:
                result = method()
            except TypeError:
                try:
                    result = method(project_id="default")
                except Exception:
                    continue
            except Exception:
                continue

            return self._normalize_collection(result)

        # Last-resort: try common attributes.
        for attr_name in ["items", "memory", "_items", "_memory"]:
            value = getattr(repository, attr_name, None)
            if value:
                return self._normalize_collection(value)

        return []

    def _normalize_collection(self, result: Any) -> list[Any]:
        if result is None:
            return []

        if isinstance(result, dict):
            for key in ["items", "memory", "results", "data", "rows"]:
                if isinstance(result.get(key), list):
                    return result[key]
            return list(result.values())

        if isinstance(result, list):
            return result

        if isinstance(result, tuple):
            return list(result)

        try:
            return list(result)
        except Exception:
            return []

    def _normalize_item(self, item: Any) -> dict[str, Any] | None:
        if item is None:
            return None

        if isinstance(item, dict):
            title = item.get("title") or item.get("name") or item.get("type") or "Memory item"
            content = (
                item.get("content")
                or item.get("description")
                or item.get("text")
                or item.get("summary")
                or item.get("value")
                or ""
            )

            if not content and title:
                content = str(title)

            return {
                "type": item.get("type") or item.get("node_type") or "fact",
                "title": str(title),
                "content": str(content),
                "description": str(content),
                "source": item.get("source") or item.get("source_ref") or "memory_repository",
                "confidence": item.get("confidence") or 0.7,
                "metadata": item.get("metadata") or {},
                "raw_item": item,
            }

        title = str(getattr(item, "title", None) or getattr(item, "name", None) or getattr(item, "type", None) or "Memory item")
        content = str(
            getattr(item, "content", None)
            or getattr(item, "description", None)
            or getattr(item, "text", None)
            or getattr(item, "summary", None)
            or title
        )

        return {
            "type": str(getattr(item, "type", None) or getattr(item, "node_type", None) or "fact"),
            "title": title,
            "content": content,
            "description": content,
            "source": str(getattr(item, "source", None) or "memory_repository"),
            "confidence": float(getattr(item, "confidence", 0.7) or 0.7),
            "raw_type": type(item).__name__,
        }


memory_graph_backfill = MemoryGraphBackfill()
