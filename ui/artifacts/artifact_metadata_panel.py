from __future__ import annotations
import streamlit as st
from services.artifact_registry_v2 import get_artifact_meta

def render_artifact_metadata_panel(artifact: dict):
    meta = get_artifact_meta(artifact.get("artifact_type", ""))
    with st.expander("Artifact details", expanded=False):
        c1, c2, c3 = st.columns(3)
        c1.metric("Category", meta.category)
        c2.metric("Status", artifact.get("status", "ready"))
        c3.metric("Format", artifact.get("format", meta.default_format))
        st.write({
            "id": artifact.get("id"),
            "extraction_id": artifact.get("extraction_id"),
            "project_id": artifact.get("project_id"),
            "artifact_type": artifact.get("artifact_type"),
            "created_at": artifact.get("created_at"),
            "metadata": artifact.get("metadata") or {},
        })
