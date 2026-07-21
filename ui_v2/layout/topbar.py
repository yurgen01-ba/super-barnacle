import streamlit as st

from repositories.workspace_repository import workspace_repository
from ui_v2.auth import get_authenticated_user, logout
from repositories.user_repository import user_repository
from ui_v2.i18n import LANGUAGE_LABELS, get_language, set_language, t
from ui_v2.pages.profile import avatar_source
from ui_v2.state import get_current_project_id, set_current_page, set_current_project


def _switch_project():
    project_id = st.session_state.get("ui_v2_topbar_project")
    if project_id:
        set_current_project(project_id)
        st.session_state.pop("selected_extraction_id", None)
        st.session_state.pop("selected_artifact_id", None)


def _cycle_language():
    languages = list(LANGUAGE_LABELS)
    current = get_language()
    language = languages[(languages.index(current) + 1) % len(languages)]
    set_language(language)
    st.session_state.pb_language_select = language
    user = get_authenticated_user() or {}
    if user.get("id"):
        user_repository.update_preferences(user["id"], language=language)


def _toggle_theme():
    theme = "light" if st.session_state.get("pb_theme", "dark") == "dark" else "dark"
    st.session_state.pb_theme = theme
    st.session_state.pb_theme_select = theme
    user = get_authenticated_user() or {}
    if user.get("id"):
        user_repository.update_preferences(user["id"], theme=theme)


def render_topbar():
    user = get_authenticated_user() or {}
    project_id = get_current_project_id()
    metrics = workspace_repository.dashboard_metrics(project_id)
    projects = workspace_repository.list_projects(user["id"])
    project_ids = [project["id"] for project in projects]
    project_names = {project["id"]: project["name"] for project in projects}
    st.session_state["ui_v2_topbar_project"] = project_id

    with st.container(key="pb_topbar"):
        project_col, status_col, preferences_col, user_col = st.columns(
            [0.34, 0.18, 0.12, 0.36],
            vertical_alignment="center",
        )
        with project_col:
            st.selectbox(
                t("project"),
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
                    <span class="pb-muted">{t('knowledge_health')}</span>
                    <span class="pb-knowledge-value">{metrics['knowledge_health']}%</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with preferences_col:
            with st.container(key="pb_topbar_preferences"):
                language_col, theme_col = st.columns(2, gap=None, vertical_alignment="center")
                with language_col:
                    current_language = get_language()
                    st.button(
                        "🌐",
                        key="pb_language_cycle",
                        help=f"{t('language')}: {t('language_' + current_language)}",
                        on_click=_cycle_language,
                    )
                with theme_col:
                    theme = st.session_state.get("pb_theme", "dark")
                    st.button(
                        "☀" if theme == "dark" else "☾",
                        key="pb_theme_toggle",
                        help=t("switch_to_light" if theme == "dark" else "switch_to_dark"),
                        on_click=_toggle_theme,
                    )
        with user_col:
            user = get_authenticated_user() or {}
            avatar_col, name_col = st.columns([0.25, 0.75], vertical_alignment="center")
            with avatar_col:
                st.image(avatar_source(user), width=38)
            with name_col:
                if st.button(
                    user.get("name") or user.get("email", "User"),
                    key="open_user_profile",
                    width="stretch",
                    help=t("profile"),
                ):
                    set_current_page("profile")
                    st.rerun()
            if st.button(t("logout"), key="auth_logout", width="stretch"):
                logout()
