from __future__ import annotations
import json
import streamlit as st
from services.artifact_registry_v2 import get_artifact_meta
from ui.artifact_download_button import render_artifact_download_button

def render_artifact_viewer(artifact: dict):
    meta = get_artifact_meta(artifact.get("artifact_type", ""))
    st.subheader(f"{meta.icon} {artifact.get('title') or meta.title}")
    st.caption(artifact.get("description") or meta.description)
    c1, c2, c3 = st.columns([1, 1, 2])
    c1.caption(f"Type: {artifact.get('artifact_type')}")
    c2.caption(f"Format: {artifact.get('format')}")
    with c3:
        render_artifact_download_button(artifact)
    content = artifact.get("content") or ""
    query = st.text_input("Search inside artifact", key=f"artifact_search_{artifact['id']}")
    if query:
        content = "\n".join(line for line in content.splitlines() if query.lower() in line.lower())
    if (artifact.get("format") or meta.default_format) == "json":
        try:
            st.json(json.loads(content.replace("'", '"')))
        except Exception:
            st.text_area("Content", content, height=560)
    else:
        st.text_area("Content", content, height=560, key=f"artifact_view_{artifact['id']}")
    with st.expander("Artifact metadata", expanded=False):
        st.json(artifact.get("metadata") or {})
