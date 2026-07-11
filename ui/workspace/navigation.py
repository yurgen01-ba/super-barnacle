import streamlit as st


WORKSPACE_AREAS = [
    "📥 Inputs / Sources",
    "📤 Outputs / Artifacts",
    "🧠 Project Model",
]


def render_workspace_selector():
    return st.radio(
        "Workspace area",
        options=WORKSPACE_AREAS,
        horizontal=True,
        label_visibility="collapsed",
        key="workspace_area_selector",
    )

