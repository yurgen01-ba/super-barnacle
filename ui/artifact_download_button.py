from __future__ import annotations
import streamlit as st

def render_artifact_download_button(artifact: dict):
    filename = f"{artifact['artifact_type']}_{artifact['id'][:8]}.txt"
    st.download_button(
        label="Download",
        data=artifact.get("content") or "",
        file_name=filename,
        mime="text/plain",
        key=f"download_{artifact['id']}",
    )
