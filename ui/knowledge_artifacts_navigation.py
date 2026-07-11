from __future__ import annotations
import streamlit as st
from ui.extraction_history import render_extraction_history

def render_knowledge_artifacts_navigation(project_id: str = "default"):
    st.header("Knowledge Artifacts")
    tab_history, tab_help = st.tabs(["Extraction History", "How to use"])
    with tab_history:
        render_extraction_history(project_id=project_id)
    with tab_help:
        st.markdown("""
### Knowledge Artifacts

After each processing job, Project Brain creates an Extraction Report.

Artifacts include:
- Transcript
- Clean Transcript
- Screen Timeline
- Extracted Knowledge
- Rejected Facts
- Ontology Mapping
- Project Model
- Summary Diff
- Prompt and final answer
""")
