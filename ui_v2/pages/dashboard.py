import streamlit as st

from ui.confluence import render_confluence_tab
from ui.jira import render_jira_tab
from ui.meetings import render_meetings_tab
from ui.slack import render_slack_tab
from ui_v2.state import get_dashboard_loader, set_dashboard_loader


def _latest_changes():
    st.markdown(
        """
        <div class="pb-panel">
            <div class="pb-panel-title">Последние изменения</div>
            <div class="pb-caption">Монитор активности проекта и изменений модели</div>
            <div class="pb-change-row">
                <div class="pb-muted">10:42</div><div>Funding process updated</div><div class="pb-tag">Process</div>
            </div>
            <div class="pb-change-row">
                <div class="pb-muted">09:15</div><div>Merchant actor added</div><div class="pb-tag">Actor</div>
            </div>
            <div class="pb-change-row">
                <div class="pb-muted">08:33</div><div>14 новых фактов извлечено</div><div class="pb-tag">Fact</div>
            </div>
            <div class="pb-change-row">
                <div class="pb-yellow">08:12</div><div>Обнаружено противоречие в Rule R27</div><div class="pb-tag">Rule</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _source_card(title: str, caption: str, button_label: str, key: str, loader: str):
    st.markdown(
        f"""
        <div class="pb-source-card">
            <div class="pb-source-title">{title}</div>
            <div class="pb-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(button_label, key=key, width="stretch"):
        set_dashboard_loader(loader)
        st.rerun()


def _render_dashboard_loader(memory_repository):
    loader = get_dashboard_loader()

    if not loader:
        st.info("Выберите карточку источника выше, чтобы открыть рабочий загрузчик прямо на Dashboard.")
        return

    title_by_loader = {
        "meetings": "🎥 Meetings loader",
        "slack": "💬 Slack importer",
        "confluence": "📚 Confluence importer",
        "jira": "🎫 Jira importer",
    }

    st.markdown(f"#### {title_by_loader.get(loader, 'Data loader')}")

    col_close, _ = st.columns([0.18, 0.82])
    with col_close:
        if st.button("Close loader", key="close_dashboard_loader", width="stretch"):
            set_dashboard_loader(None)
            st.rerun()

    if loader == "meetings":
        render_meetings_tab(memory_repository)
    elif loader == "slack":
        render_slack_tab(memory_repository)
    elif loader == "confluence":
        render_confluence_tab(memory_repository)
    elif loader == "jira":
        render_jira_tab(memory_repository)


def render_dashboard(memory_repository):
    st.title("Дашборд")
    st.caption("Обзор состояния проекта и загрузка данных")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Состояние знаний", "91%", "+7% за 7 дней")

    with col2:
        st.metric("Источники данных", "6", "+2 новых")

    with col3:
        st.metric("Артефактов создано", "28", "+5 за неделю")

    _latest_changes()

    st.markdown("### Загрузка данных")
    st.caption("Карточки ниже открывают существующие рабочие загрузчики внутри нового Dashboard.")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        _source_card("🎥 Meetings", "Видео/аудио встреч, транскрипт, vision и facts.", "Открыть", "dash_upload_meeting", "meetings")
    with c2:
        _source_card("💬 Slack", "Импорт сообщений и обсуждений.", "Открыть", "dash_import_slack", "slack")
    with c3:
        _source_card("📚 Confluence", "Страницы, статьи и документация.", "Открыть", "dash_import_confluence", "confluence")
    with c4:
        _source_card("🎫 Jira", "Задачи, комментарии и статусы.", "Открыть", "dash_import_jira", "jira")

    with st.expander("Active data loader", expanded=get_dashboard_loader() is not None):
        _render_dashboard_loader(memory_repository)

    st.caption("✅ Последняя синхронизация: 2 мин назад")
