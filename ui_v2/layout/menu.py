import streamlit as st
from ui_v2.assets import logo_data_uri
from ui_v2.i18n import t
from ui_v2.state import (
    get_current_page,
    open_artifacts,
    open_source,
    set_current_page,
)


def _nav(label: str, page: str):
    active = get_current_page() == page
    if st.button(
        label,
        key=f"ui_v2_nav_{page}",
        width="stretch",
        type="primary" if active else "secondary",
    ):
        st.session_state.pb_page_transition = True
        set_current_page(page)
        st.rerun()


def _source_nav(label: str, source: str):
    active = get_current_page() == "sources" and st.session_state.get("ui_v2_selected_source") == source
    if st.button(
        label,
        key=f"ui_v2_source_{source}",
        width="stretch",
        type="primary" if active else "secondary",
    ):
        st.session_state.pb_page_transition = True
        open_source(source)
        st.rerun()


def render_menu():
    logo = logo_data_uri()
    st.markdown(
        f"""
        <div class="pb-brand">
            <div class="pb-brand-logo"><img src="{logo}" alt="Project Brain"></div>
            <div><div class="pb-brand-title">Project Brain</div>
            <div class="pb-caption">AI Business Analyst</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(key="pb_navigation"):
        _nav(t("projects"), "projects")
        _nav(t("workspace"), "dashboard")
        _nav(t("sources"), "sources")
        _nav(t("participants"), "participants")
        _nav(t("speech_quality"), "transcription_diagnostics")
        if st.button(
            t("artifacts"),
            key="ui_v2_nav_artifacts",
            width="stretch",
            type="primary" if get_current_page() == "artifacts" else "secondary",
        ):
            open_artifacts()
            st.rerun()
        _nav(t("exports"), "exports")

        st.caption(t("source_section"))
        _source_nav(t("meetings"), "meetings")
        _source_nav("Slack", "slack")
        _source_nav("Confluence", "confluence")
        _source_nav("Jira", "jira")
        _source_nav(t("files"), "files")

        st.caption(t("project_section"))
        _nav(t("settings"), "settings")
        _nav(t("project_model"), "project_model")
