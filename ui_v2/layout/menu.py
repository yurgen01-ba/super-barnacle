import streamlit as st

from repositories.workspace_repository import DEFAULT_PROJECT_ID, workspace_repository
from ui_v2.state import (
    get_current_page,
    get_current_project_id,
    open_artifacts,
    open_source,
    set_current_page,
    set_current_project,
)


def _nav(label: str, icon: str, page: str):
    is_active = get_current_page() == page
    button_type = "primary" if is_active else "secondary"

    if st.button(f"{icon}  {label}", key=f"ui_v2_nav_{page}", width="stretch", type=button_type):
        set_current_page(page)
        st.rerun()


def _source_nav(label: str, source: str):
    if st.button(label, key=f"ui_v2_source_{source}", width="stretch"):
        open_source(source)
        st.rerun()


def render_menu():
    current_project_id = get_current_project_id()
    current_project = workspace_repository.get_project(current_project_id)
    st.markdown(
        """
        <div class="pb-panel">
            <div class="pb-panel-title">🧠 Project Brain</div>
            <div class="pb-caption">AI Business Analyst workspace</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _nav("Дашборд", "🏠", "dashboard")

    st.divider()

    _nav("Sources", "📥", "sources")
    _nav("Transcription Quality", "🎙️", "transcription_diagnostics")
    if st.button("📦  Knowledge Artifacts", key="ui_v2_nav_artifacts", width="stretch", type="primary" if get_current_page() == "artifacts" else "secondary"):
        open_artifacts()
        st.rerun()

    st.markdown(
        """
        <div class="pb-menu-block">
            <div class="pb-menu-block-title">Sources menu</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _source_nav("🎥 Meetings", "meetings")
    _source_nav("💬 Slack", "slack")
    _source_nav("📚 Confluence", "confluence")
    _source_nav("🎫 Jira", "jira")
    _source_nav("📁 Files", "files")

    st.divider()

    with st.expander("＋  Добавить проект", expanded=False):
        with st.form("ui_v2_add_project_form", clear_on_submit=True):
            new_project_name = st.text_input("Название проекта")
            if st.form_submit_button("Создать", width="stretch"):
                try:
                    project = workspace_repository.create_project(new_project_name)
                    set_current_project(project["id"])
                    st.success("Проект создан")
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))

    st.markdown(
        """
        <div class="pb-menu-block">
            <div class="pb-menu-block-title">Project menu</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("⚙ Настройки проекта", key="ui_v2_project_settings", width="stretch"):
        set_current_page("settings")
        st.rerun()

    st.button("👥 Участники", key="ui_v2_project_members", width="stretch", disabled=True)

    if st.button("🧬 Модель проекта · Beta", key="ui_v2_project_model", width="stretch"):
        set_current_page("project_model")
        st.rerun()

    st.button("⬇ Экспорт данных", key="ui_v2_project_export", width="stretch", disabled=True)
    if current_project_id != DEFAULT_PROJECT_ID:
        with st.expander("🗑 Удалить проект", expanded=False):
            st.warning("Источники, события и артефакты этого проекта будут удалены.")
            confirmation = st.text_input(
                "Введите УДАЛИТЬ",
                key="ui_v2_delete_project_confirmation",
            )
            if st.button(
                "Удалить безвозвратно",
                key="ui_v2_project_delete",
                width="stretch",
                disabled=confirmation != "УДАЛИТЬ",
            ):
                workspace_repository.delete_project(current_project_id)
                set_current_project(DEFAULT_PROJECT_ID)
                st.rerun()

    st.divider()

    st.markdown(
        f"""
        <div class="pb-project-card">
            <div class="pb-project-card-row">
                <div>
                    <div class="pb-project-label">Текущий проект</div>
                    <div class="pb-project-name">{current_project['name']}</div>
                </div>
                <div class="pb-small-button">⋯</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
