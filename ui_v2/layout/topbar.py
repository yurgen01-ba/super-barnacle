import streamlit as st

from repositories.workspace_repository import workspace_repository
from ui_v2.state import get_current_project_id, set_current_project


def render_topbar():
    projects = workspace_repository.list_projects()
    project_ids = [item["id"] for item in projects]
    current_id = get_current_project_id()
    current_index = project_ids.index(current_id) if current_id in project_ids else 0

    selected_id = st.selectbox(
        "Текущий проект",
        project_ids,
        index=current_index,
        format_func=lambda value: next(
            (item["name"] for item in projects if item["id"] == value), value
        ),
        key="ui_v2_project_switcher",
    )
    if selected_id != current_id:
        set_current_project(selected_id)
        st.session_state.pop("selected_extraction_id", None)
        st.session_state.pop("selected_artifact_id", None)
        st.rerun()

    metrics = workspace_repository.dashboard_metrics(selected_id)
    st.markdown(
        f"""
        <div class="pb-topbar">
            <div class="pb-row">
                <div>
                    <span class="pb-muted">Рабочее пространство проекта</span>
                </div>
                <div style="display:flex;gap:1rem;align-items:center;">
                    <span class="pb-muted">Состояние знаний</span>
                    <span style="border:2px solid #3B82F6;border-radius:999px;padding:0.45rem 0.4rem;color:white;font-size:0.78rem;">{metrics['knowledge_health']}%</span>
                    <span><span style="color:#22C55E;">●</span> Активно</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
