from __future__ import annotations
from repositories.artifact_repository import artifact_repository

class ArtifactSearchEngine:
    def search_extraction(self, extraction_id: str, query: str) -> list[dict]:
        artifacts = artifact_repository.list_by_extraction(extraction_id)
        q = (query or "").lower().strip()
        if not q:
            return artifacts
        results = []
        for artifact in artifacts:
            text = f"{artifact.get('title','')} {artifact.get('description','')} {artifact.get('content','')}".lower()
            if q in text:
                item = dict(artifact)
                item["match_count"] = text.count(q)
                results.append(item)
        return sorted(results, key=lambda x: x.get("match_count", 0), reverse=True)

artifact_search_engine = ArtifactSearchEngine()
