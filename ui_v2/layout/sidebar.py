import streamlit as st

from ui_v2.state import get_current_page, set_current_page


def _nav(label: str, icon: str, page: str):
    is_active = get_current_page() == page
    button_type = "primary" if is_active else "secondary"

    if st.button(
        f"{icon}  {label}",
        key=f"nav_{page}",
        width="stretch",
        type=button_type,
    ):
        set_current_page(page)
        st.rerun()


def render_sidebar():
    st.markdown("<div class='pb-left-menu'>", unsafe_allow_html=True)

    st.markdown("<div class='pb-sidebar-brand'>◇ Project Brain</div>", unsafe_allow_html=True)

    _nav("Дашборд", "🏠", "dashboard")

    st.divider()

    _nav("Sources", "📥", "sources")

    with st.expander("Sources menu", expanded=True):
        st.caption("Meetings")
        st.caption("Slack")
        st.caption("Confluence")
        st.caption("Jira")
        st.caption("Files")

    st.divider()

    st.button("＋  Добавить проект", key="add_project_button", width="stretch", disabled=True)
    st.markdown("<div class='pb-nonfunctional'>Coming next: project creation flow.</div>", unsafe_allow_html=True)

    with st.expander("⋯ Project menu", expanded=False):
        if st.button("⚙ Настройки проекта", key="project_settings", width="stretch"):
            set_current_page("settings")
            st.rerun()

        st.button("👥 Участники", key="project_members", width="stretch", disabled=True)

        if st.button("⬡ Модель проекта · Beta", key="project_model_beta", width="stretch"):
            set_current_page("project_model")
            st.rerun()

        st.button("⬇ Экспорт данных", key="project_export", width="stretch", disabled=True)
        st.button("🗑 Удалить проект", key="project_delete", width="stretch", disabled=True)

    st.divider()

    st.markdown(
        """
        <div class="pb-card">
            <div class="pb-card-caption">Текущий проект</div>
            <div style="font-size:1rem;font-weight:700;color:#FAFAFA;margin-top:0.25rem;">OrgMeter</div>
            <div class="pb-card-caption" style="margin-top:0.4rem;">Advanced model access is in Project menu.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)
