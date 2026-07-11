from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from graph.graph_types import EdgeType
from models.knowledge_edge import KnowledgeEdge
from models.knowledge_node import KnowledgeNode
from ontology.ontology_resolver import ontology_resolver
from repositories.project_graph_store import project_graph_store


@dataclass(slots=True)
class FactGraphBuildResult:
    facts: int = 0
    actors: int = 0
    processes: int = 0
    entities: int = 0
    integrations: int = 0
    sources: int = 0
    edges: int = 0
    dropped_unknown: int = 0
    created_nodes: list[KnowledgeNode] = field(default_factory=list)


def _slug(text: str) -> str:
    safe = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(text or ""))
    safe = "_".join(part for part in safe.split("_") if part)
    return safe[:90] or "unknown"


class FactGraphBuilder:
    """
    Builds Project Graph using OntologyResolver.

    It no longer creates arbitrary actors/processes/entities by loose keyword match.
    Only canonical domain terms become model nodes.
    """

    def build_from_items(
        self,
        items: list[dict[str, Any]],
        project_id: str = "default",
        source: str = "fact_graph_builder",
    ) -> FactGraphBuildResult:
        result = FactGraphBuildResult()

        for index, raw_item in enumerate(items, start=1):
            if not isinstance(raw_item, dict):
                continue

            item = ontology_resolver.normalize_fact(raw_item)
            text = self._item_text(item)
            if not text.strip():
                continue

            resolved_items = ontology_resolver.resolve_fact(item)

            # Keep fact node only if it resolves to at least one canonical ontology item.
            if not resolved_items:
                result.dropped_unknown += 1
                continue

            fact_node = self._save_fact_node(item, text, index, project_id, source)
            result.facts += 1
            result.created_nodes.append(fact_node)

            source_node = self._save_source_node(item, project_id, source)
            if source_node:
                result.sources += 1
                result.created_nodes.append(source_node)
                self._save_edge(fact_node.id, source_node.id, EdgeType.DERIVED_FROM, project_id, source)
                result.edges += 1

            ontology_nodes = []
            for resolved in resolved_items:
                node = self._save_ontology_node(resolved, project_id, source)
                ontology_nodes.append(node)
                result.created_nodes.append(node)

                if resolved.node_type == "actor":
                    result.actors += 1
                elif resolved.node_type == "process":
                    result.processes += 1
                elif resolved.node_type == "integration":
                    result.integrations += 1
                else:
                    result.entities += 1

                self._save_edge(fact_node.id, node.id, EdgeType.RELATES_TO, project_id, source)
                result.edges += 1

            self._connect_ontology_nodes(ontology_nodes, project_id, source, result)

        return result

    def _item_text(self, item: dict[str, Any]) -> str:
        values = [
            item.get("title"),
            item.get("content"),
            item.get("description"),
            item.get("text"),
            item.get("subject"),
            item.get("predicate"),
            item.get("object"),
        ]
        return " ".join(str(value) for value in values if value)

    def _save_fact_node(self, item: dict[str, Any], text: str, index: int, project_id: str, source: str) -> KnowledgeNode:
        title = str(item.get("title") or item.get("subject") or f"Fact {index}")
        source_id = str(item.get("source_id") or item.get("source_ref") or item.get("source") or "")
        node_id = f"fact:{_slug(title)}:{abs(hash(text))}"

        node = KnowledgeNode(
            id=node_id,
            node_type="fact",
            title=title,
            description=text,
            confidence=float(item.get("confidence") or 0.7),
            status=str(item.get("status") or "active"),
            source=str(item.get("source") or source),
            source_id=source_id,
            metadata={
                "project_id": project_id,
                "raw_item": item,
                "ontology_resolved": True,
            },
        )
        return project_graph_store.save_node(node, project_id=project_id)

    def _save_source_node(self, item: dict[str, Any], project_id: str, source: str) -> KnowledgeNode | None:
        source_title = str(item.get("source") or item.get("source_ref") or item.get("source_document_id") or source).strip()
        if not source_title:
            return None

        node = KnowledgeNode(
            id=f"source:{_slug(source_title)}",
            node_type="source",
            title=source_title,
            description=f"Source detected from project facts: {source_title}",
            confidence=1.0,
            status="active",
            source=source,
            source_id=source_title,
            metadata={"project_id": project_id},
        )
        return project_graph_store.save_node(node, project_id=project_id)

    def _save_ontology_node(self, resolved, project_id: str, source: str) -> KnowledgeNode:
        node = KnowledgeNode(
            id=f"{resolved.node_type}:{_slug(resolved.canonical)}",
            node_type=resolved.node_type,
            title=resolved.canonical,
            description=resolved.metadata.get("term_description") or f"Canonical {resolved.node_type}: {resolved.canonical}",
            confidence=resolved.confidence,
            status="active",
            source=source,
            metadata={
                "project_id": project_id,
                "ru_label": resolved.ru_label,
                "en_label": resolved.en_label,
                "canonical": resolved.canonical,
                "source_text": resolved.source_text[:500],
            },
        )
        return project_graph_store.save_node(node, project_id=project_id)

    def _connect_ontology_nodes(self, nodes: list[KnowledgeNode], project_id: str, source: str, result: FactGraphBuildResult):
        actors = [node for node in nodes if node.node_type == "actor"]
        processes = [node for node in nodes if node.node_type == "process"]
        entities = [node for node in nodes if node.node_type == "entity"]
        integrations = [node for node in nodes if node.node_type == "integration"]

        for actor in actors:
            for process in processes:
                self._save_edge(actor.id, process.id, EdgeType.PARTICIPATES_IN, project_id, source)
                result.edges += 1

        for process in processes:
            for entity in entities:
                self._save_edge(process.id, entity.id, EdgeType.AFFECTS, project_id, source)
                result.edges += 1

        for integration in integrations:
            for entity in entities + processes:
                self._save_edge(integration.id, entity.id, EdgeType.RELATES_TO, project_id, source)
                result.edges += 1

    def _save_edge(self, from_node_id: str, to_node_id: str, relationship_type: str, project_id: str, source: str) -> KnowledgeEdge:
        edge = KnowledgeEdge(
            id=f"edge:{from_node_id}:{relationship_type}:{to_node_id}",
            from_node_id=from_node_id,
            to_node_id=to_node_id,
            relationship_type=relationship_type,
            confidence=0.75,
            source=source,
            metadata={"project_id": project_id},
        )
        return project_graph_store.save_edge(edge, project_id=project_id)
