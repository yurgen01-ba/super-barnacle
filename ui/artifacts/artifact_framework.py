from __future__ import annotations
import streamlit as st
from repositories.extraction_repository import extraction_repository
from services.artifact_api import artifact_api
from services.artifact_registry_v2 import group_artifacts
from ui.artifacts.artifact_download_center import render_artifact_download_center
from ui.artifacts.artifact_metadata_panel import render_artifact_metadata_panel
from ui.artifacts.artifact_navigation import render_artifact_breadcrumbs, set_selected_artifact
from ui.artifacts.artifact_viewer_framework import render_artifact_viewer

def render_artifact_framework(project_id: str = "default"):
    st.header("Artifacts")
    extractions = extraction_repository.list(project_id=project_id, limit=100)
    if not extractions:
        st.info("No extractions yet.")
        return

    selected_extraction_id = st.session_state.get("selected_extraction_id")
    default_index = 0
    if selected_extraction_id:
        for idx, item in enumerate(extractions):
            if item.get("id") == selected_extraction_id:
                default_index = idx
                break

    extraction = st.selectbox(
        "Extraction",
        extractions,
        index=default_index,
        format_func=lambda e: f"{e['source_name']} · {e['status']} · {e['started_at']}",
    )
    st.session_state["selected_extraction_id"] = extraction["id"]
    render_artifact_breadcrumbs(extraction=extraction)

    query = st.text_input("Search artifacts")
    artifacts = artifact_api.search_artifacts(extraction["id"], query) if query else artifact_api.list_artifacts(extraction["id"])

    for category, items in group_artifacts(artifacts).items():
        st.subheader(category.title())
        cols = st.columns(3)
        for idx, artifact in enumerate(items):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"**{artifact['title']}**")
                    st.caption(artifact.get("description") or artifact["artifact_type"])
                    if st.button("Open", key=f"fw_open_{artifact['id']}"):
                        set_selected_artifact(artifact["id"])

    selected_id = st.session_state.get("selected_artifact_id")
    if not selected_id:
        return
    artifact = artifact_api.get_artifact(extraction["id"], selected_id)
    if not artifact:
        return
    st.divider()
    render_artifact_breadcrumbs(extraction=extraction, artifact=artifact)
    render_artifact_viewer(artifact)
    render_artifact_metadata_panel(artifact)
    render_artifact_download_center(artifact)
