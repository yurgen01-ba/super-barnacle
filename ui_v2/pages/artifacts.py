from __future__ import annotations

import streamlit as st

from ui_v2.adapters.artifact_adapters import render_artifact_framework_v2
from ui_v2.state import get_current_project_id
from ui_v2.i18n import t


def render_artifacts(project_id: str | None = None):
    project_id = project_id or get_current_project_id()
    st.title(t("knowledge_artifacts"))
    st.caption(t("knowledge_artifacts_caption"))
    render_artifact_framework_v2(project_id=project_id)
