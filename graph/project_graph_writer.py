from __future__ import annotations

from typing import Any

from graph.node_normalizer import normalize_to_node
from graph.graph_types import EdgeType
from models.knowledge_edge import KnowledgeEdge
from repositories.project_graph_store import project_graph_store


class ProjectGraphWriter:
    """
    Adapter for writing extracted/built project model objects into ProjectGraphStore.

    Existing builders can call this without changing their internal extraction logic.
    """

    def save_items(self, items: list[Any], default_type: str = "fact", source: str = "builder") -> dict:
        saved = []

        for index, item in enumerate(items, start=1):
            node = normalize_to_node(
                item=item,
                node_type=self._infer_type(item, default_type),
                source=source,
                fallback_index=index,
            )
            project_graph_store.save_node(node)
            saved.append(node)

        return {
            "saved": len(saved),
            "nodes": saved,
        }

    def save_relation(
        self,
        from_node_id: str,
        to_node_id: str,
        relationship_type: str = EdgeType.RELATES_TO,
        confidence: float = 0.7,
        source: str = "builder",
    ) -> KnowledgeEdge:
        edge = KnowledgeEdge(
            id=f"edge:{from_node_id}:{relationship_type}:{to_node_id}",
            from_node_id=from_node_id,
            to_node_id=to_node_id,
            relationship_type=relationship_type,
            confidence=confidence,
            source=source,
        )
        return project_graph_store.save_edge(edge)

    @staticmethod
    def _infer_type(item: Any, default_type: str) -> str:
        if isinstance(item, dict):
            return str(item.get("type") or item.get("node_type") or default_type)

        return str(
            getattr(item, "type", None)
            or getattr(item, "node_type", None)
            or default_type
        )
