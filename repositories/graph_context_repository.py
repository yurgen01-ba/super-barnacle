from __future__ import annotations

from graph.graph_intent import GraphIntent, detect_graph_intent
from graph.graph_query_engine import GraphContext, GraphQueryEngine
from graph.graph_repository import GraphRepository
from graph.project_overview_retriever import ProjectOverviewRetriever
from repositories.graph_repository_factory import build_default_graph_repository


class GraphContextRepository:
    def __init__(self, graph_repository: GraphRepository | None = None):
        self.graph_repository = graph_repository or build_default_graph_repository()
        self.query_engine = GraphQueryEngine(self.graph_repository)
        self.overview_retriever = ProjectOverviewRetriever(self.graph_repository)

    def get_context(self, question: str, refresh: bool = False) -> GraphContext:
        return self.query_engine.get_context(
            query=question,
            limit=12,
            related_limit=8,
            refresh=refresh,
        )

    def build_prompt_context(self, question: str, refresh: bool = False) -> str:
        intent = detect_graph_intent(question)

        if intent == GraphIntent.PROJECT_OVERVIEW:
            if refresh:
                self.graph_repository.get_graph(refresh=True)
            return self.overview_retriever.build_context()

        return self.get_context(question=question, refresh=refresh).to_prompt_context()

    def stats(self, refresh: bool = False) -> dict[str, int]:
        return self.graph_repository.stats(refresh=refresh)
