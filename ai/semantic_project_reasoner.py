from __future__ import annotations

from graph.graph_retriever_v2 import GraphRetrieverV2


class SemanticProjectReasoner:
    """
    First reasoning boundary over Project Graph.

    This is intentionally lightweight:
    - retrieves graph context;
    - prepares reasoning-oriented context;
    - does not use chunk-based RAG.
    """

    def __init__(self, graph_retriever: GraphRetrieverV2 | None = None):
        self.graph_retriever = graph_retriever or GraphRetrieverV2()

    def analyze_impact(self, change_description: str) -> str:
        retrieved = self.graph_retriever.retrieve(change_description)

        return f"""
PROJECT GRAPH IMPACT ANALYSIS CONTEXT

Change:
{change_description}

Intent:
{retrieved.intent}

Graph statistics:
{retrieved.stats}

Relevant Project Graph context:
{retrieved.context}
""".strip()
