from __future__ import annotations
import json
import streamlit as st

def render_artifact_download_center(artifact: dict):
    content = artifact.get("content") or ""
    base = f"{artifact.get('artifact_type','artifact')}_{artifact.get('id','')[:8]}"
    with st.expander("Download options", expanded=False):
        st.download_button("Download TXT", data=content, file_name=f"{base}.txt", mime="text/plain")
        st.download_button("Download Markdown", data=content, file_name=f"{base}.md", mime="text/markdown")
        st.download_button("Download JSON", data=json.dumps(artifact, ensure_ascii=False, indent=2), file_name=f"{base}.json", mime="application/json")
