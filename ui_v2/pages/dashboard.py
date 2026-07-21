import streamlit as st
from ui_v2.i18n import t

from ui.confluence import render_confluence_tab
from ui.jira import render_jira_tab
from ui.meetings import render_meetings_tab
from ui.slack import render_slack_tab
from repositories.workspace_repository import workspace_repository
from ui_v2.state import get_current_project_id, get_dashboard_loader, set_dashboard_loader


def _latest_changes(project_id: str):
    st.subheader("Последние изменения")
    st.caption("Важные события проекта. Раскройте строку, чтобы увидеть полный журнал.")
    events = workspace_repository.list_events(project_id, limit=20)
    if not events:
        st.info("Событий пока нет. Загрузите первый источник данных.")
        return

    icons = {
        "source": "▧",
        "extraction": "◌",
        "artifact": "▣",
        "settings": "⚙︎",
        "project": "◇",
    }
    for event in events:
        created_at = str(event.get("created_at") or "")
        label = (
            f"{icons.get(event['event_type'], '•')} "
            f"{created_at[:16]} · {event['title']}"
        )
        with st.expander(label, expanded=False):
            st.caption(f"Тип события: {event['event_type']}")
            details = event.get("details") or {}
            if details:
                st.json(details)
            else:
                st.text("Дополнительных данных нет")


def _source_card(title: str, caption: str, key: str, loader: str):
    st.markdown(
        f"""
        <div class="pb-source-card">
            <div class="pb-source-title">{title}</div>
            <div class="pb-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    is_open = get_dashboard_loader() == loader
    if st.button("Свернуть" if is_open else "Открыть", key=key, width="stretch"):
        set_dashboard_loader(None if is_open else loader)
        st.rerun()


def _render_dashboard_loader(memory_repository):
    loader = get_dashboard_loader()

    title_by_loader = {
        "meetings": "Meetings loader",
        "slack": "Slack importer",
        "confluence": "Confluence importer",
        "jira": "Jira importer",
    }

    st.markdown(f"#### {title_by_loader.get(loader, 'Data loader')}")

    if loader == "meetings":
        render_meetings_tab(memory_repository)
    elif loader == "slack":
        render_slack_tab(memory_repository)
    elif loader == "confluence":
        render_confluence_tab(memory_repository)
    elif loader == "jira":
        render_jira_tab(memory_repository)


def render_dashboard(memory_repository):
    project_id = get_current_project_id()
    metrics = workspace_repository.dashboard_metrics(project_id)
    st.title(t("workspace"))
    st.caption("Обзор состояния проекта и загрузка данных")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Состояние знаний",
            f"{metrics['knowledge_health']}%",
            f"{metrics['knowledge_items']} элементов знаний",
            help="Расчёт учитывает количество источников, извлечённых элементов знаний и готовых артефактов.",
        )

    with col2:
        st.metric("Источники данных", str(metrics["sources"]), "в текущем проекте")

    with col3:
        st.metric("Артефактов создано", str(metrics["artifacts"]), "готовы к просмотру")

    _latest_changes(project_id)

    st.markdown("### Загрузка данных")
    st.caption("Карточки ниже открывают существующие рабочие загрузчики внутри нового Dashboard.")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        _source_card("Встречи", "Видео/аудио встреч, транскрипт, vision и facts.", "dash_upload_meeting", "meetings")
    with c2:
        _source_card("Slack", "Импорт сообщений и обсуждений.", "dash_import_slack", "slack")
    with c3:
        _source_card("Confluence", "Страницы, статьи и документация.", "dash_import_confluence", "confluence")
    with c4:
        _source_card("Jira", "Задачи, комментарии и статусы.", "dash_import_jira", "jira")

    if get_dashboard_loader() is not None:
        with st.container(border=True, key="dashboard_active_loader"):
            _render_dashboard_loader(memory_repository)
