from __future__ import annotations

from collections import Counter

from repositories.project_graph_store import project_graph_store


DOMAIN_OVERVIEW = """
OrgMeter is a financing / advance management system. It supports merchant advances,
funders, ISOs, referrers, syndicators, underwriting, payback allocation, fees,
payout history, funder migration, reports, notes and integrations such as Equifax/Bizcap.
""".strip()


class ProjectSummaryContextBuilder:
    """
    Builds stable summary-first context for broad project questions.

    It prevents answers from becoming a random list of raw facts.
    """

    def build(self, project_id: str = "default", limit_facts: int = 20) -> str:
        graph = project_graph_store.get_graph(project_id, hydrate=False)

        actors = self._nodes("actor", project_id)
        processes = self._nodes("process", project_id)
        entities = self._nodes("entity", project_id)
        facts = self._nodes("fact", project_id)
        sources = self._nodes("source", project_id)

        lines = []
        lines.append("PROJECT SUMMARY CONTEXT")
        lines.append("")
        lines.append("Known domain baseline:")
        lines.append(DOMAIN_OVERVIEW)
        lines.append("")
        lines.append("Graph statistics:")
        for key, value in sorted(graph.stats().items()):
            lines.append(f"- {key}: {value}")

        lines.append("")
        lines.append("High-level interpretation:")
        lines.append("- Treat OrgMeter as a financial operations platform around merchant advances, funders, payments/paybacks, fees and reporting.")
        lines.append("- Use graph facts as supporting evidence, not as a random bullet list.")
        lines.append("- Ignore obviously corrupted speech-recognition fragments unless they match canonical domain terms.")

        self._append_group(lines, "Core actors", actors)
        self._append_group(lines, "Core processes", processes)
        self._append_group(lines, "Core entities", entities)
        self._append_group(lines, "Sources", sources)

        lines.append("")
        lines.append("Representative facts:")
        for node in self._rank_facts(facts)[:limit_facts]:
            lines.append(f"- {node.description[:400]}")

        return "\n".join(lines)

    def _nodes(self, node_type: str, project_id: str):
        graph = project_graph_store.get_graph(project_id, hydrate=False)
        return [
            node for node in graph.nodes.values()
            if node.node_type == node_type and node.metadata.get("project_id", project_id) == project_id
        ]

    def _append_group(self, lines: list[str], title: str, nodes):
        lines.append("")
        lines.append(f"{title}:")
        if not nodes:
            lines.append("- Not confidently detected yet.")
            return

        for node in sorted(nodes, key=lambda n: (-float(n.confidence or 0), n.title.lower()))[:30]:
            lines.append(f"- {node.title}")

    def _rank_facts(self, facts):
        bad_terms = {"речьек", "совосились", "ферфлайс", "элосии"}
        filtered = [
            fact for fact in facts
            if not any(term in fact.description.lower() for term in bad_terms)
        ]
        return sorted(filtered, key=lambda node: (-float(node.confidence or 0), node.title.lower()))
