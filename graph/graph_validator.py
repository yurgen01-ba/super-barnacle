from graph.graph_types import KnowledgeGraph


def validate_graph(graph: KnowledgeGraph) -> list[str]:
    issues: list[str] = []

    for edge in graph.edges:
        if edge.from_node_id not in graph.nodes:
            issues.append(f"Edge {edge.id} has missing from_node_id: {edge.from_node_id}")

        if edge.to_node_id not in graph.nodes:
            issues.append(f"Edge {edge.id} has missing to_node_id: {edge.to_node_id}")

        if edge.from_node_id == edge.to_node_id:
            issues.append(f"Edge {edge.id} is self-referential")

    return issues
