import streamlit as st
from ui_v2.state import (
    get_current_page,
    open_artifacts,
    open_source,
    set_current_page,
)


def _nav(label: str, glyph: str, page: str):
    active = get_current_page() == page
    if st.button(
        f"{glyph}  {label}",
        key=f"ui_v2_nav_{page}",
        width="stretch",
        type="primary" if active else "secondary",
    ):
        set_current_page(page)
        st.rerun()


def _source_nav(label: str, glyph: str, source: str):
    active = get_current_page() == "sources" and st.session_state.get("ui_v2_selected_source") == source
    if st.button(
        f"{glyph}  {label}",
        key=f"ui_v2_source_{source}",
        width="stretch",
        type="primary" if active else "secondary",
    ):
        open_source(source)
        st.rerun()


def render_menu():
    st.markdown(
        """
        <div class="pb-brand">
            <div class="pb-brand-mark">PB</div>
            <div><div class="pb-brand-title">Project Brain</div>
            <div class="pb-caption">AI Business Analyst</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(key="pb_navigation"):
        st.caption("РАБОЧЕЕ ПРОСТРАНСТВО")
        _nav("Проекты", "◇", "projects")
        _nav("Дашборд", "⌂", "dashboard")
        _nav("Источники", "≡", "sources")
        _nav("Качество речи", "◌", "transcription_diagnostics")
        if st.button(
            "▣  Артефакты",
            key="ui_v2_nav_artifacts",
            width="stretch",
            type="primary" if get_current_page() == "artifacts" else "secondary",
        ):
            open_artifacts()
            st.rerun()
        _nav("Экспорт данных", "⇩", "exports")

        st.caption("ИСТОЧНИКИ")
        _source_nav("Встречи", "▷", "meetings")
        _source_nav("Slack", "□", "slack")
        _source_nav("Confluence", "▤", "confluence")
        _source_nav("Jira", "▱", "jira")
        _source_nav("Файлы", "▧", "files")

        st.caption("ПРОЕКТ")
        _nav("Настройки", "⚙︎", "settings")
        _nav("Модель проекта", "⬡", "project_model")
