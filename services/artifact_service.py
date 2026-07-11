from __future__ import annotations
from models.artifact import KnowledgeArtifact
from models.extraction import Extraction
from repositories.artifact_repository import artifact_repository
from repositories.extraction_repository import extraction_repository

class ArtifactService:
    def start_extraction(self, source_id: str, source_name: str, source_type: str, project_id: str = "default") -> Extraction:
        return extraction_repository.save(Extraction.create(source_id=source_id, source_name=source_name, source_type=source_type, project_id=project_id))

    def save_artifact(self, extraction_id: str, project_id: str, artifact_type: str, title: str, content: str, description: str = "", format: str = "text", metadata: dict | None = None) -> KnowledgeArtifact:
        artifact = KnowledgeArtifact.create(extraction_id=extraction_id, project_id=project_id, artifact_type=artifact_type, title=title, content=content, description=description, format=format, metadata=metadata or {})
        return artifact_repository.save(artifact)

    def complete_extraction(self, extraction: Extraction, statistics: dict | None = None) -> Extraction:
        artifact_count = len(artifact_repository.list_by_extraction(extraction.id))
        extraction.complete(artifact_count=artifact_count, statistics=statistics or {})
        return extraction_repository.save(extraction)

artifact_service = ArtifactService()
