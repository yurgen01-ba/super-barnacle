from graph.graph_types import KnowledgeGraph


def graph_to_dict(graph: KnowledgeGraph) -> dict:
    return {
        "nodes": [node.to_dict() for node in graph.nodes.values()],
        "edges": [edge.to_dict() for edge in graph.edges],
        "stats": graph.stats(),
    }


def graph_to_markdown(graph: KnowledgeGraph) -> str:
    lines = ["# Knowledge Graph", ""]

    stats = graph.stats()
    lines.append("## Stats")
    for key, value in stats.items():
        lines.append(f"- {key}: {value}")

    lines.append("")
    lines.append("## Nodes")
    for node in graph.nodes.values():
        lines.append(f"- [{node.node_type}] {node.title} ({node.id})")

    lines.append("")
    lines.append("## Edges")
    for edge in graph.edges:
        lines.append(
            f"- {edge.from_node_id} --{edge.relationship_type}--> {edge.to_node_id}"
        )

    return "\n".join(lines)
