from __future__ import annotations
from repositories.artifact_repository import artifact_repository
from services.artifact_search_engine import artifact_search_engine

class ArtifactAPI:
    def list_artifacts(self, extraction_id: str) -> list[dict]:
        return artifact_repository.list_by_extraction(extraction_id)
    def get_artifact(self, extraction_id: str, artifact_id: str) -> dict | None:
        return next((a for a in artifact_repository.list_by_extraction(extraction_id) if a.get("id") == artifact_id), None)
    def search_artifacts(self, extraction_id: str, query: str) -> list[dict]:
        return artifact_search_engine.search_extraction(extraction_id, query)

artifact_api = ArtifactAPI()
