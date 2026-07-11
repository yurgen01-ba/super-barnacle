from __future__ import annotations
import streamlit as st
from repositories.extraction_repository import extraction_repository
from ui.extraction_report import render_extraction_report

def render_extraction_history(project_id: str = "default"):
    st.header("Extraction History")
    extractions = extraction_repository.list(project_id=project_id, limit=100)
    if not extractions:
        st.info("No extractions yet.")
        return

    for extraction in extractions:
        with st.expander(f"{extraction['source_name']} · {extraction['status']} · artifacts: {extraction['artifact_count']}", expanded=False):
            st.write(extraction)
            render_extraction_report(extraction)
