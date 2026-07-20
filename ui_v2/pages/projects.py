from __future__ import annotations

from html import escape

import streamlit as st

from repositories.workspace_repository import workspace_repository
from ui_v2.state import get_current_project_id, set_current_page, set_current_project


def _enter_project(project_id: str):
    set_current_project(project_id)
    set_current_page("dashboard")
    st.session_state.pop("selected_extraction_id", None)
    st.session_state.pop("selected_artifact_id", None)


def render_projects():
    st.title("Проекты")
    st.caption("Создавайте рабочие пространства и управляйте существующими проектами.")

    with st.form("projects_create_form", clear_on_submit=True):
        col_name, col_action = st.columns([0.72, 0.28])
        with col_name:
            name = st.text_input("Новый проект", placeholder="Название проекта")
        with col_action:
            st.write("")
            st.write("")
            create = st.form_submit_button("Создать проект", type="primary", width="stretch")
        if create:
            try:
                project = workspace_repository.create_project(name)
                _enter_project(project["id"])
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

    projects = workspace_repository.list_projects()
    current_id = get_current_project_id()
    st.subheader("Список проектов")

    st.markdown(
        """
        <div class="pb-project-table">
            <div class="pb-project-table-head">
                <span>Проект</span><span>Источники</span><span>Артефакты</span>
                <span>Знания</span><span>Действия</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for project in projects:
        project_id = project["id"]
        metrics = workspace_repository.dashboard_metrics(project_id)
        with st.container(key=f"pb_project_row_{project_id}"):
            name_col, sources_col, artifacts_col, knowledge_col, action_col = st.columns(
                [2.2, 0.75, 0.75, 0.75, 1.0], vertical_alignment="center"
            )
            with name_col:
                badge = '<span class="pb-current-badge">открыт</span>' if project_id == current_id else ""
                st.markdown(
                    f'<div class="pb-table-project-name">{escape(project["name"])}{badge}</div>',
                    unsafe_allow_html=True,
                )
            with sources_col:
                st.markdown(f'<div class="pb-table-cell">{metrics["sources"]}</div>', unsafe_allow_html=True)
            with artifacts_col:
                st.markdown(f'<div class="pb-table-cell">{metrics["artifacts"]}</div>', unsafe_allow_html=True)
            with knowledge_col:
                st.markdown(f'<div class="pb-table-cell">{metrics["knowledge_health"]}%</div>', unsafe_allow_html=True)
            with action_col:
                if st.button(
                    "Открыть" if project_id != current_id else "Открыт",
                    key=f"project_enter_{project_id}",
                    type="primary" if project_id != current_id else "secondary",
                    width="stretch",
                    disabled=project_id == current_id,
                ):
                    _enter_project(project_id)
                    st.rerun()

            with st.expander("Управление", expanded=False):
                with st.form(f"project_rename_form_{project_id}"):
                    renamed = st.text_input(
                        "Новое название",
                        value=project["name"],
                        key=f"project_rename_value_{project_id}",
                    )
                    if st.form_submit_button("Переименовать"):
                        workspace_repository.rename_project(project_id, renamed)
                        st.rerun()

                if len(projects) > 1:
                    confirmation = st.text_input(
                        "Для удаления введите УДАЛИТЬ",
                        key=f"project_delete_confirmation_{project_id}",
                    )
                    if st.button(
                        "Удалить проект",
                        key=f"project_delete_{project_id}",
                        disabled=confirmation != "УДАЛИТЬ",
                    ):
                        fallback = next(item["id"] for item in projects if item["id"] != project_id)
                        workspace_repository.delete_project(project_id)
                        if current_id == project_id:
                            set_current_project(fallback)
                        st.rerun()
                else:
                    st.caption("Нельзя удалить единственный проект.")
