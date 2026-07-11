from __future__ import annotations
from services.artifact_service import artifact_service

class ProjectModelArtifactBuilder:
    def build(self, extraction_id: str, project_id: str = "default", **payload):
        title = payload.get("title") or "Project Model"
        content = payload.get("content") or payload.get("text") or ""
        description = payload.get("description") or "Generated project model artifact."
        return artifact_service.save_artifact(
            extraction_id=extraction_id,
            project_id=project_id,
            artifact_type="project_model",
            title=title,
            description=description,
            content=content,
            format=payload.get("format") or "markdown",
            metadata=payload.get("metadata") or {},
        )

projectModelArtifactBuilder = ProjectModelArtifactBuilder()
