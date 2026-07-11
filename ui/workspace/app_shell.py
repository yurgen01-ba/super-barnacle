import streamlit as st

from memory.db import init_db
from memory.fact_schema import init_fact_schema
from repositories.memory_repository import MemoryRepository
from ui.design import inject_project_brain_theme
from ui.floating_project_chat import render_floating_project_chat
from ui.workspace.artifacts import render_artifacts_area
from ui.workspace.header import render_header
from ui.workspace.model import render_project_model_area
from ui.workspace.navigation import render_workspace_selector
from ui.workspace.sources import render_sources_area


def initialize_app():
    st.set_page_config(
        page_title="Project Brain 3.0",
        page_icon="🧠",
        layout="wide",
    )

    inject_project_brain_theme()

    init_db()
    init_fact_schema()

    return MemoryRepository()


def render_app_shell():
    memory_repository = initialize_app()

    render_header()

    render_floating_project_chat(memory_repository)

    st.divider()

    area = render_workspace_selector()

    st.divider()

    if area == "📥 Inputs / Sources":
        render_sources_area(memory_repository)
    elif area == "📤 Outputs / Artifacts":
        render_artifacts_area(memory_repository)
    else:
        render_project_model_area(memory_repository)

