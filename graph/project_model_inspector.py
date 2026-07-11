from __future__ import annotations

from graph.knowledge_inspector import KnowledgeInspector
from repositories.graph_context_repository import GraphContextRepository


class ProjectModelInspector:
    """
    Backend API for advanced Project Model view.

    UI can call this to inspect graph stats, nodes and node profiles.
    """

    def __init__(self, context_repository: GraphContextRepository | None = None):
        self.context_repository = context_repository or GraphContextRepository()
        self.inspector = KnowledgeInspector(self.context_repository.graph_repository)

    def stats(self) -> dict[str, int]:
        return self.context_repository.stats()

    def search(self, query: str, limit: int = 20) -> list[dict]:
        profiles = self.inspector.search_profiles(query=query, limit=limit)
        return [profile.to_dict() for profile in profiles]

    def profile_markdown(self, node_id: str) -> str:
        return self.inspector.get_profile(node_id).to_markdown()
