from __future__ import annotations

import streamlit as st

from ui_v2.adapters.artifact_adapters import render_artifact_framework_v2


def render_artifacts(project_id: str = "default"):
    st.title("Knowledge Artifacts")
    st.caption("Extraction reports, transcripts, screen analysis, facts, ontology mapping and project model snapshots.")
    render_artifact_framework_v2(project_id=project_id)
