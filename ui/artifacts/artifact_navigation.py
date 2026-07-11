from __future__ import annotations
import streamlit as st

def render_artifact_breadcrumbs(extraction: dict | None = None, artifact: dict | None = None):
    parts = ["Project", "Extractions"]
    if extraction:
        parts.append(extraction.get("source_name") or extraction.get("id"))
    if artifact:
        parts.append(artifact.get("title") or artifact.get("artifact_type"))
    st.caption(" / ".join(parts))

def set_selected_artifact(artifact_id: str):
    st.session_state["selected_artifact_id"] = artifact_id

def clear_selected_artifact():
    st.session_state.pop("selected_artifact_id", None)
