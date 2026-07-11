from __future__ import annotations
from services.artifact_service import artifact_service

class KnowledgeArtifactBuilder:
    def build(self, extraction_id: str, project_id: str = "default", **payload):
        title = payload.get("title") or "Knowledge"
        content = payload.get("content") or payload.get("text") or ""
        description = payload.get("description") or "Generated knowledge artifact."
        return artifact_service.save_artifact(
            extraction_id=extraction_id,
            project_id=project_id,
            artifact_type="knowledge",
            title=title,
            description=description,
            content=content,
            format=payload.get("format") or "markdown",
            metadata=payload.get("metadata") or {},
        )

knowledgeArtifactBuilder = KnowledgeArtifactBuilder()
