from __future__ import annotations

import streamlit as st

from ui_v2.pages.artifacts import render_artifacts
from ui_v2.pages.transcription_diagnostics import render_transcription_diagnostics
from ui_v2.pages.dashboard import render_dashboard
from ui_v2.pages.project_model import render_project_model
from ui_v2.pages.settings import render_settings
from ui_v2.pages.sources import render_sources
from ui_v2.pages.projects import render_projects
from ui_v2.pages.exports import render_exports
from ui_v2.pages.profile import render_profile
from ui_v2.pages.participants import render_participants
from ui_v2.state import get_current_page


PAGE_TITLES = {
    "dashboard": "Dashboard",
    "sources": "Sources",
    "artifacts": "Knowledge Artifacts",
    "project_model": "Project Model",
    "settings": "Settings",
    "projects": "Projects",
    "exports": "Data Export",
    "profile": "Profile",
    "participants": "Participants",
}


def render_current_page(memory_repository):
    page = get_current_page()

    if page == "dashboard":
        render_dashboard(memory_repository)
    elif page == "sources":
        render_sources(memory_repository)
    elif page == "artifacts":
        render_artifacts()
    elif page == "transcription_diagnostics":
        render_transcription_diagnostics()
    elif page == "project_model":
        render_project_model(memory_repository)
    elif page == "settings":
        render_settings()
    elif page == "projects":
        render_projects()
    elif page == "exports":
        render_exports()
    elif page == "profile":
        render_profile()
    elif page == "participants":
        render_participants()
    else:
        st.warning(f"Unknown page: {page}. Opening Dashboard.")
        render_dashboard(memory_repository)
