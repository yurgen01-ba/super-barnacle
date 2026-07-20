from __future__ import annotations

from typing import Any

from ai.transcript_cleaner import clean_transcript_text, is_low_value_transcript
from builders.project_summary_builder_v2 import project_summary_builder_v2
from graph.fact_graph_builder import FactGraphBuilder
from graph.graph_diagnostics import graph_diagnostics
from graph.project_graph_hydration import project_graph_hydration_service
from pipeline.canonical_facts_pipeline import CanonicalFactsPipeline
from repositories.memory_repository import MemoryRepository
from repositories.persistent_project_graph_repository import persistent_project_graph_repository
from repositories.project_graph_store import project_graph_store
from repositories.transcript_segment_repository import transcript_segment_repository


class TranscriptSegmentPersistence:
    def __init__(self):
        self.memory_repository = MemoryRepository()
        self.canonical_pipeline = CanonicalFactsPipeline()
        self.fact_graph_builder = FactGraphBuilder()

    def save_segment(
        self,
        file_name: str,
        source: str,
        segment_no: int,
        total_segments: int,
        text: str,
        project_id: str = "default",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        raw_text = text or ""
        cleaned_text = clean_transcript_text(raw_text)

        if is_low_value_transcript(cleaned_text):
            return {"saved": False, "reason": "low_value_segment", "segment_no": segment_no}

        segment = transcript_segment_repository.save_segment(
            source=source,
            file_name=file_name,
            segment_no=segment_no,
            total_segments=total_segments,
            text=cleaned_text,
            project_id=project_id,
            metadata={**(metadata or {}), "raw_text": raw_text, "cleaned": True},
        )

        memory_item = {
            "type": "transcript_segment",
            "title": f"{file_name} — transcript segment {segment_no}/{total_segments}",
            "content": cleaned_text,
            "description": cleaned_text,
            "source": source,
            "confidence": 0.8,
            "metadata": {
                "segment_id": segment.id,
                "segment_no": segment_no,
                "total_segments": total_segments,
                "file_name": file_name,
                "cleaned": True,
                **(metadata or {}),
            },
        }

        memory_repository = MemoryRepository(project_id=project_id)
        saved, skipped, errors = memory_repository.save_items([memory_item], default_source=source)

        canonical_result = self.canonical_pipeline.process_extracted_items(
            source_type="transcript_segment",
            title=memory_item["title"],
            original_text=cleaned_text,
            extracted_items=[memory_item],
            project_id=project_id,
            source_ref=segment.id,
        )

        stats_after_save = persistent_project_graph_repository.stats(project_id)
        project_graph_hydration_service.hydrate(project_id)
        hydrated_stats = project_graph_store.get_graph(project_id).stats()

        summary = project_summary_builder_v2.build_and_save(project_id)

        graph_diagnostics.record(
            "segment_persistence:summary_updated",
            "Project summary updated after transcript segment",
            project_id=project_id,
            counts={
                "summary_actors": len(summary.actors),
                "summary_processes": len(summary.processes),
                "summary_entities": len(summary.entities),
                "summary_integrations": len(summary.integrations),
                "persistent_nodes": stats_after_save.get("nodes", 0),
                "hydrated_nodes": hydrated_stats.get("nodes", 0),
            },
        )

        return {
            "saved": True,
            "segment": segment,
            "memory": {"saved": saved, "skipped": skipped, "errors": errors},
            "canonical_result": canonical_result,
            "persistent_graph_stats": stats_after_save,
            "hydrated_graph_stats": hydrated_stats,
            "project_summary": summary.to_dict(),
        }


def make_transcript_segment_callback(file_name: str, source: str, project_id: str = "default"):
    persistence = TranscriptSegmentPersistence()

    def callback(event: dict):
        if not isinstance(event, dict):
            return None

        if event.get("event") != "audio_segment_completed":
            return None

        text = event.get("text") or event.get("transcript") or event.get("segment_text") or ""
        current = int(event.get("current") or event.get("segment_no") or 1)
        total = int(event.get("total") or event.get("total_segments") or current)

        return persistence.save_segment(
            file_name=file_name,
            source=source,
            segment_no=current,
            total_segments=total,
            text=text,
            project_id=project_id,
            metadata={key: value for key, value in event.items() if key not in {"text", "transcript", "segment_text"}},
        )

    return callback
