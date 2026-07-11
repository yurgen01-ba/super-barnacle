from __future__ import annotations
from services.artifact_service import artifact_service

class TranscriptArtifactBuilder:
    def build(self, extraction_id: str, project_id: str = "default", **payload):
        title = payload.get("title") or "Transcript"
        content = payload.get("content") or payload.get("text") or ""
        description = payload.get("description") or "Generated transcript artifact."
        return artifact_service.save_artifact(
            extraction_id=extraction_id,
            project_id=project_id,
            artifact_type="transcript",
            title=title,
            description=description,
            content=content,
            format=payload.get("format") or "markdown",
            metadata=payload.get("metadata") or {},
        )

transcriptArtifactBuilder = TranscriptArtifactBuilder()
