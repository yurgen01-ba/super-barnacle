import streamlit as st

from memory.db import init_db
from memory.fact_schema import init_fact_schema
from repositories.memory_repository import MemoryRepository
from repositories.workspace_repository import workspace_repository
from ui_v2.assets import favicon_image
from ui_v2.atlassian import render_atlassian_oauth_callback
from ui_v2.slack_oauth import render_slack_oauth_callback
from ui_v2.auth import get_authenticated_user, render_auth_gate
from ui_v2.design import inject_ui_v2_theme
from ui_v2.i18n import set_language, t
from ui_v2.layout.chat import render_chat_panel
from ui_v2.layout.menu import render_menu
from ui_v2.layout.topbar import render_topbar, render_user_controls
from ui_v2.loaders import render_intro_loader, render_transition_loader
from ui_v2.job_activity import render_active_job_activity
from ui_v2.pages.page_registry import render_current_page
from ui_v2.state import get_current_project_id, set_current_page, set_current_project
from jobs.job_recovery import resume_incomplete_jobs


def _render_project_onboarding(user: dict) -> None:
    @st.dialog(t("create_first_project"), width="medium")
    def _dialog() -> None:
        st.caption(t("create_first_project_caption"))
        with st.form("first_project_form"):
            project_name = st.text_input(
                t("project_name"), placeholder=t("project_name_placeholder"),
                key="first_project_name",
            )
            submitted = st.form_submit_button(
                t("create_project_and_continue"), type="primary", width="stretch"
            )
        if submitted:
            try:
                project = workspace_repository.create_project(
                    project_name,
                    user["id"],
                    user.get("email", ""),
                    user.get("name", ""),
                )
            except ValueError:
                st.error(t("project_name_required"))
                return
            set_current_project(project["id"])
            set_current_page("dashboard")
            st.rerun()

    _dialog()


def render_app_shell_v2():
    st.set_page_config(
        page_title="Project Brain",
        page_icon=favicon_image(),
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    user = get_authenticated_user() or {}
    if user and st.session_state.get("pb_preferences_user") != user.get("id"):
        if user.get("preferred_language"):
            set_language(user["preferred_language"])
        if user.get("preferred_theme") in {"dark", "light"}:
            st.session_state.pb_theme = user["preferred_theme"]
        st.session_state.pb_preferences_user = user.get("id")

    inject_ui_v2_theme(st.session_state.get("pb_theme", "dark"))

    # Resume durable background work as soon as the Streamlit process serves a
    # session; recovery must not depend on the user opening a particular page.
    init_db()
    init_fact_schema()
    resume_incomplete_jobs()

    if render_atlassian_oauth_callback():
        return
    if render_slack_oauth_callback():
        return

    if not render_auth_gate():
        return

    user = get_authenticated_user() or {}
    workspace_repository.ensure_user_workspace(
        user["id"], user.get("email", ""), user.get("name", ""), create_if_missing=False
    )
    if not workspace_repository.list_projects(user["id"]):
        _render_project_onboarding(user)
        return

    if not st.session_state.get("pb_intro_seen"):
        render_intro_loader(duration=3.55)
        st.session_state.pb_intro_seen = True

    if st.session_state.pop("pb_page_transition", False):
        render_transition_loader()

    project_id = get_current_project_id()
    memory_repository = MemoryRepository(project_id=project_id)
    render_active_job_activity(project_id)
    menu_col, main_col, chat_col = st.columns([0.18, 0.58, 0.24], gap="large")

    with menu_col:
        render_menu()

    with main_col:
        render_topbar()
        render_current_page(memory_repository)

    with chat_col:
        render_user_controls()
        render_chat_panel(memory_repository)
