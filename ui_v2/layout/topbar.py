import streamlit as st

from repositories.workspace_repository import workspace_repository
from ui_v2.auth import get_authenticated_user, logout
from ui_v2.state import get_current_project_id, set_current_project


def _switch_project():
    project_id = st.session_state.get("ui_v2_topbar_project")
    if project_id:
        set_current_project(project_id)
        st.session_state.pop("selected_extraction_id", None)
        st.session_state.pop("selected_artifact_id", None)


def render_topbar():
    project_id = get_current_project_id()
    metrics = workspace_repository.dashboard_metrics(project_id)
    projects = workspace_repository.list_projects()
    project_ids = [project["id"] for project in projects]
    project_names = {project["id"]: project["name"] for project in projects}
    st.session_state["ui_v2_topbar_project"] = project_id

    with st.container(key="pb_topbar"):
        project_col, status_col, user_col = st.columns([0.58, 0.25, 0.17], vertical_alignment="center")
        with project_col:
            st.selectbox(
                "Проект",
                project_ids,
                index=project_ids.index(project_id),
                format_func=lambda value: project_names[value],
                key="ui_v2_topbar_project",
                on_change=_switch_project,
            )
        with status_col:
            st.markdown(
                f"""
                <div class="pb-knowledge-indicator">
                    <span class="pb-muted">Состояние знаний</span>
                    <span class="pb-knowledge-value">{metrics['knowledge_health']}%</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with user_col:
            user = get_authenticated_user() or {}
            st.caption(user.get("email", ""))
            if st.button("Выйти", key="auth_logout", width="stretch"):
                logout()
