from __future__ import annotations
import streamlit as st

def render_transcript_viewer(artifact: dict):
    st.header("Transcript Viewer")
    st.caption(artifact.get("description") or artifact.get("artifact_type"))
    query = st.text_input("Search", key=f"search_{artifact.get('id')}")
    content = artifact.get("content") or ""
    if query:
        lines = [line for line in content.splitlines() if query.lower() in line.lower()]
        st.caption(f"Matches: {len(lines)}")
        st.text_area("Search results", "\n".join(lines), height=360)
    else:
        st.text_area("Content", content, height=560)
