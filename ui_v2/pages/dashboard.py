import streamlit as st
from ui_v2.i18n import t

from ui.confluence import render_confluence_tab
from ui.jira import render_jira_tab
from ui.meetings import render_meetings_tab
from ui.slack import render_slack_tab
from repositories.workspace_repository import workspace_repository
from ui_v2.state import get_current_project_id, get_dashboard_loader, set_dashboard_loader


def _latest_changes(project_id: str):
    st.subheader(t("recent_changes"))
    st.caption(t("recent_changes_caption"))
    events = workspace_repository.list_events(project_id, limit=20)
    if not events:
        st.info(t("no_events"))
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
        raw_title = str(event.get("title") or "")
        if raw_title.startswith("Добавлен источник:"):
            event_title = t("event_source_added", name=raw_title.split(":", 1)[1].strip())
        else:
            event_title = t(
                {
                    "Проект создан": "event_project_created",
                    "Проект переименован": "event_project_renamed",
                    "Настройки проекта обновлены": "event_settings_updated",
                    "Запущена обработка файлов": "event_files_started",
                    "Обработаны загруженные файлы": "event_files_processed",
                    "Созданы артефакты расшифровки": "event_transcript_artifacts",
                    "Запущена обработка видео": "event_video_started",
                    "AI-артефакт создан": "event_ai_artifact_created",
                }.get(raw_title, "event_unknown"),
                default=raw_title,
            )
        label = (
            f"{icons.get(event['event_type'], '•')} "
            f"{created_at[:16]} · {event_title}"
        )
        with st.expander(label, expanded=False):
            st.caption(f"{t('event_type')}: {event['event_type']}")
            details = event.get("details") or {}
            if details:
                st.json(details)
            else:
                st.text(t("no_event_details"))


def _source_card(title: str, caption: str, loader: str):
    is_open = get_dashboard_loader() == loader
    state = "active" if is_open else "idle"
    if st.button(
        title,
        key=f"pb_source_card_{loader}_{state}",
        help=caption,
        width="stretch",
    ):
        set_dashboard_loader(None if is_open else loader)
        st.rerun()


def _render_dashboard_loader(memory_repository):
    loader = get_dashboard_loader()

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
    st.caption(t("workspace_caption"))

    col1, col2, col3 = st.columns(3)

    with col1:
        knowledge_help = t(
            "knowledge_health_help",
            total=metrics["knowledge_health"],
            sources=metrics["sources"],
            source_score=metrics["source_score"],
            knowledge=metrics["knowledge_items"],
            knowledge_score=metrics["knowledge_score"],
            artifacts=metrics["artifacts"],
            artifact_score=metrics["artifact_score"],
        )
        st.metric(
            t("knowledge_health"),
            f"{metrics['knowledge_health']}%",
            f"{metrics['knowledge_items']} элементов знаний",
            help=knowledge_help,
        )

    with col2:
        st.metric(t("data_sources"), str(metrics["sources"]), t("in_current_project"))

    with col3:
        st.metric(t("artifacts_created"), str(metrics["artifacts"]), t("ready_to_view"))

    _latest_changes(project_id)

    st.markdown(f"### {t('data_upload')}")
    st.caption(t("data_upload_caption"))

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        _source_card(
            t("meetings"), t("meetings_card"), "meetings",
        )
    with c2:
        _source_card("Slack", t("slack_card"), "slack")
    with c3:
        _source_card(
            "Confluence", t("confluence_card"), "confluence",
        )
    with c4:
        _source_card("Jira", t("jira_card"), "jira")

    if get_dashboard_loader() is not None:
        with st.container(border=True, key="dashboard_active_loader"):
            _render_dashboard_loader(memory_repository)
