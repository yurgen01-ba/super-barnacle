from __future__ import annotations
import streamlit as st

def render_artifact_cards(artifacts: list[dict]):
    if not artifacts:
        st.info("No artifacts available.")
        return

    cols = st.columns(3)
    for idx, artifact in enumerate(artifacts):
        with cols[idx % 3]:
            with st.container(border=True):
                st.markdown(f"### {_icon(artifact['artifact_type'])} {artifact['title']}")
                st.caption(artifact.get("description") or artifact["artifact_type"])
                st.caption(f"Format: {artifact.get('format')} · Status: {artifact.get('status')}")
                if st.button("Open", key=f"artifact_card_open_{artifact['id']}"):
                    st.session_state["selected_artifact_id"] = artifact["id"]

def _icon(t: str) -> str:
    return {"transcript":"📝","clean_transcript":"✨","screen_timeline":"📷","knowledge":"🧠","ontology_mapping":"🔗","project_model":"📊"}.get(t,"📦")
