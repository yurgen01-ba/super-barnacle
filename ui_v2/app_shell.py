import streamlit as st
from memory.db import init_db
from memory.fact_schema import init_fact_schema
from repositories.memory_repository import MemoryRepository
from repositories.workspace_repository import workspace_repository
from ui_v2.design import inject_ui_v2_theme
from ui_v2.auth import get_authenticated_user, render_auth_gate
from ui_v2.i18n import set_language
from ui_v2.layout.chat import render_chat_panel
from ui_v2.layout.menu import render_menu
from ui_v2.layout.topbar import handle_user_control_actions, render_topbar, render_user_controls
from ui_v2.pages.page_registry import render_current_page
from ui_v2.state import get_current_project_id
from ui_v2.loaders import render_intro_loader, render_transition_loader


def render_app_shell_v2():
    st.set_page_config(
        page_title="Project Brain",
        page_icon="🦭",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    inject_ui_v2_theme(st.session_state.get("pb_theme", "dark"))

    if not render_auth_gate():
        return

    handle_user_control_actions()

    user = get_authenticated_user() or {}
    workspace_repository.ensure_user_workspace(
        user["id"], user.get("email", ""), user.get("name", "")
    )
    if st.session_state.get("pb_preferences_user") != user.get("id"):
        if user.get("preferred_language"):
            set_language(user["preferred_language"])
        if user.get("preferred_theme") in {"dark", "light"}:
            st.session_state.pb_theme = user["preferred_theme"]
        st.session_state.pb_preferences_user = user.get("id")
    inject_ui_v2_theme(st.session_state.get("pb_theme", "dark"))

    if not st.session_state.get("pb_intro_seen"):
        render_intro_loader(duration=2.8)
        st.session_state.pb_intro_seen = True

    if st.session_state.pop("pb_page_transition", False):
        render_transition_loader()

    init_db()
    init_fact_schema()

    memory_repository = MemoryRepository(project_id=get_current_project_id())

    menu_col, main_col, chat_col = st.columns([0.18, 0.58, 0.24], gap="large")

    with menu_col:
        render_menu()

    with main_col:
        render_topbar()
        render_current_page(memory_repository)

    with chat_col:
        render_user_controls()
        render_chat_panel(memory_repository)
