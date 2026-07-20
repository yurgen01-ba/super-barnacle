import streamlit as st

from repositories.workspace_repository import workspace_repository
from ui_v2.state import get_current_project_id


def render_topbar():
    project_id = get_current_project_id()
    project = workspace_repository.get_project(project_id)
    metrics = workspace_repository.dashboard_metrics(project_id)
    st.markdown(
        f"""
        <div class="pb-topbar">
            <div class="pb-row">
                <div>
                    <span class="pb-muted">Проект</span>
                    <span class="pb-topbar-project">{project['name']}</span>
                </div>
                <div class="pb-knowledge-indicator">
                    <span class="pb-muted">Состояние знаний</span>
                    <span class="pb-knowledge-value">{metrics['knowledge_health']}%</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
