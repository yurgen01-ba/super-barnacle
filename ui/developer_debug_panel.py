from __future__ import annotations
import streamlit as st
from repositories.artifact_repository import artifact_repository

DEBUG_TYPES = {"prompt", "reasoning_context", "final_answer", "logs", "rejected_facts"}

def render_developer_debug_panel(extraction_id: str):
    with st.expander("Developer artifacts", expanded=False):
        artifacts = [a for a in artifact_repository.list_by_extraction(extraction_id) if a["artifact_type"] in DEBUG_TYPES]
        if not artifacts:
            st.caption("No developer artifacts.")
            return
        for artifact in artifacts:
            with st.expander(artifact["title"]):
                st.text_area("Content", artifact.get("content",""), height=360, key=f"debug_{artifact['id']}")
