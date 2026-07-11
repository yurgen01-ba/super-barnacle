from __future__ import annotations

import streamlit as st

from repositories.artifact_repository import artifact_repository
from services.artifact_registry_v2 import group_artifacts, get_artifact_meta
from ui.artifacts.artifact_viewer_framework import render_artifact_viewer


def render_extraction_report(extraction: dict):
    st.subheader("Knowledge Extraction Report")
    st.caption(f"{extraction.get('source_name')} · {extraction.get('status')} · Artifacts: {extraction.get('artifact_count', 0)}")

    artifacts = artifact_repository.list_by_extraction(extraction["id"])
    if not artifacts:
        st.info("No artifacts generated yet.")
        return

    for category, items in group_artifacts(artifacts).items():
        st.markdown(f"### {category.title()} artifacts")
        cols = st.columns(3)
        for idx, artifact in enumerate(items):
            meta = get_artifact_meta(artifact.get("artifact_type", ""))
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"**{meta.icon} {artifact.get('title') or meta.title}**")
                    st.caption(artifact.get("description") or meta.description)
                    st.caption(f"{artifact.get('format')} · {artifact.get('status')}")
                    if st.button("Open", key=f"report_open_{artifact['id']}"):
                        st.session_state["selected_report_artifact_id"] = artifact["id"]

    selected_id = st.session_state.get("selected_report_artifact_id")
    selected = next((artifact for artifact in artifacts if artifact["id"] == selected_id), None)

    if selected:
        st.divider()
        render_artifact_viewer(selected)
