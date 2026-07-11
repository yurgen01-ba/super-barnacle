from __future__ import annotations
import streamlit as st
from repositories.extraction_repository import extraction_repository
from ui.artifacts.artifact_explorer import render_artifact_explorer

def render_extraction_workspace(project_id: str = "default"):
    st.header("Extraction Workspace")
    extractions = extraction_repository.list(project_id=project_id, limit=100)
    if not extractions:
        st.info("No extractions yet.")
        return
    selected = st.selectbox(
        "Extraction",
        extractions,
        format_func=lambda e: f"{e.get('source_name')} · {e.get('status')} · {e.get('started_at')}",
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Status", selected.get("status", "unknown"))
    c2.metric("Artifacts", selected.get("artifact_count", 0))
    c3.metric("Source", selected.get("source_type", "unknown"))
    duration = selected.get("duration_seconds")
    c4.metric("Duration", f"{round(duration, 1)}s" if duration else "—")
    with st.expander("Extraction metadata", expanded=False):
        st.json(selected)
    render_artifact_explorer(selected["id"], project_id=project_id)
