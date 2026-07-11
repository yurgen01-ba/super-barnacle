from __future__ import annotations

from repositories.project_graph_store import project_graph_store


class EvidenceRetriever:
    """
    Retrieves only relevant supporting facts for a question.
    """

    def retrieve_evidence(self, question: str, project_id: str = "default", limit: int = 12) -> list[str]:
        graph = project_graph_store.get_graph(project_id, hydrate=False)
        q = (question or "").lower()
        terms = [term for term in q.replace("-", " ").replace("/", " ").split() if len(term) >= 3]

        scored = []

        for node in graph.nodes.values():
            if node.node_type != "fact":
                continue

            text = f"{node.title} {node.description}".lower()
            score = 0

            for term in terms:
                if term in text:
                    score += 1

            # Broad project questions: use high-confidence representative facts.
            if not terms or any(term in q for term in ["orgmeter", "проект", "overview", "describe"]):
                score += int(float(node.confidence or 0) * 10)

            if score > 0:
                scored.append((score, node))

        scored.sort(key=lambda item: (item[0], float(item[1].confidence or 0)), reverse=True)

        evidence = []
        seen = set()

        for _, node in scored:
            text = node.description.strip()
            if not text or text.lower() in seen:
                continue
            seen.add(text.lower())
            evidence.append(text[:500])
            if len(evidence) >= limit:
                break

        return evidence


evidence_retriever = EvidenceRetriever()
