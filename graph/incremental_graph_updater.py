from __future__ import annotations

from hashlib import sha256

from pipeline.canonical_facts_pipeline import CanonicalFactsPipeline
from repositories.project_graph_store import project_graph_store
from repositories.source_document_repository import source_document_repository


class IncrementalGraphUpdater:
    """
    Updates Project Graph from new source data without rebuilding everything.
    """

    def __init__(self, canonical_pipeline: CanonicalFactsPipeline | None = None):
        self.canonical_pipeline = canonical_pipeline or CanonicalFactsPipeline()
        self._processed_hashes: set[str] = set()

    def update_from_extracted_items(
        self,
        source_type: str,
        title: str,
        original_text: str,
        extracted_items: list[dict],
        project_id: str = "default",
        source_ref: str = "",
    ) -> dict:
        content_hash = sha256(original_text.encode("utf-8", errors="ignore")).hexdigest()

        if content_hash in self._processed_hashes:
            return {
                "status": "skipped",
                "reason": "source_already_processed",
                "content_hash": content_hash,
                "graph_stats": project_graph_store.get_graph(project_id).stats(),
            }

        result = self.canonical_pipeline.process_extracted_items(
            source_type=source_type,
            title=title,
            original_text=original_text,
            extracted_items=extracted_items,
            project_id=project_id,
            source_ref=source_ref,
        )

        self._processed_hashes.add(content_hash)

        return {
            "status": "updated",
            "content_hash": content_hash,
            "pipeline_result": result,
            "graph_stats": project_graph_store.get_graph(project_id).stats(),
        }
