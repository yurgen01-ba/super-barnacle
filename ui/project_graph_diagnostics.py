from __future__ import annotations

import streamlit as st

from graph.graph_diagnostics import graph_diagnostics
from graph.memory_graph_backfill import memory_graph_backfill
from graph.project_graph_hydration import project_graph_hydration_service
from repositories.project_graph_store import project_graph_store


def render_project_graph_diagnostics(project_id: str = "default"):
    st.header("Project Graph Diagnostics")

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("Hydrate graph from persistence"):
            stats = project_graph_hydration_service.hydrate(project_id, backfill_if_empty=False)
            st.success("Project Graph hydrated.")
            st.json(stats)

    with col_b:
        if st.button("Backfill graph from memory"):
            result = memory_graph_backfill.backfill(project_id=project_id, force=True)
            st.success("Backfill completed.")
            st.write(result)

    runtime_graph = project_graph_store.get_graph(project_id)
    runtime_stats = runtime_graph.stats()
    persistent_stats = project_graph_hydration_service.persisted_stats(project_id)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Runtime Graph")
        st.json(runtime_stats)

    with col2:
        st.subheader("Persistent Graph")
        st.json(persistent_stats)

    st.subheader("Nodes by type")

    node_types = sorted({node.node_type for node in runtime_graph.nodes.values()})
    selected_type = st.selectbox("Node type", options=["all"] + node_types)

    nodes = list(runtime_graph.nodes.values())
    if selected_type != "all":
        nodes = [node for node in nodes if node.node_type == selected_type]

    st.caption(f"Showing first 50 of {len(nodes)} node(s).")

    for node in nodes[:50]:
        with st.expander(f"[{node.node_type}] {node.title}", expanded=False):
            st.write({
                "id": node.id,
                "type": node.node_type,
                "title": node.title,
                "description": node.description,
                "confidence": node.confidence,
                "status": node.status,
                "source": node.source,
                "source_id": node.source_id,
                "metadata": node.metadata,
            })

    st.subheader("Edges")
    st.caption(f"Showing first 80 of {len(runtime_graph.edges)} edge(s).")

    for edge in runtime_graph.edges[:80]:
        st.code(f"{edge.from_node_id} --{edge.relationship_type}--> {edge.to_node_id}")

    st.subheader("Pipeline diagnostics")
    st.markdown(graph_diagnostics.latest_markdown(project_id=project_id, limit=80))
