from __future__ import annotations

from graph.project_graph_writer import ProjectGraphWriter
from repositories.project_graph_store import project_graph_store
from repositories.source_document_repository import source_document_repository


class UnifiedGraphBuilder:
    """
    Builds/updates Project Graph from normalized project sources and facts.

    This is the central graph build boundary for the new Project Model.
    """

    def __init__(self, graph_writer: ProjectGraphWriter | None = None):
        self.graph_writer = graph_writer or ProjectGraphWriter()

    def rebuild_from_sources(self, project_id: str = "default") -> dict:
        documents = source_document_repository.list_documents(project_id=project_id)

        source_nodes = []

        for document in documents:
            node = project_graph_store.save_node(
                node=self._document_to_node(document),
                project_id=project_id,
            )
            source_nodes.append(node)

        return {
            "project_id": project_id,
            "source_documents": len(documents),
            "source_nodes": len(source_nodes),
            "graph_stats": project_graph_store.get_graph(project_id).stats(),
        }

    @staticmethod
    def _document_to_node(document):
        from models.knowledge_node import KnowledgeNode

        return KnowledgeNode(
            id=f"source:{document.id}",
            node_type="source",
            title=document.title,
            description=document.original_text[:500],
            confidence=1.0,
            status="active",
            source=document.source_type,
            source_id=document.id,
            metadata={
                "project_id": document.project_id,
                "source_ref": document.source_ref,
                "text_hash": document.text_hash(),
            },
        )
