from __future__ import annotations

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

    for project in projects:
        project_id = project["id"]
        metrics = workspace_repository.dashboard_metrics(project_id)
        with st.container(border=True):
            title_col, enter_col = st.columns([0.72, 0.28])
            with title_col:
                current_label = " · открыт" if project_id == current_id else ""
                st.markdown(f"### {project['name']}{current_label}")
                st.caption(
                    f"Источников: {metrics['sources']} · "
                    f"Артефактов: {metrics['artifacts']} · "
                    f"Состояние знаний: {metrics['knowledge_health']}%"
                )
            with enter_col:
                if st.button(
                    "Войти в проект",
                    key=f"project_enter_{project_id}",
                    type="primary" if project_id != current_id else "secondary",
                    width="stretch",
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
