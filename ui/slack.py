import streamlit as st

from jobs.extraction_tasks import process_slack_text_job
from jobs.knowledge_extraction_service import KnowledgeExtractionJobService
from repositories.memory_repository import MemoryRepository
from repositories.workspace_repository import workspace_repository
from ui.job_status import render_job_status
from ui_v2.state import get_current_project_id, is_job_result_dismissed
from ui_v2.auth import get_authenticated_email
from ui_v2.i18n import t
from ui_v2.source_connections import render_source_authorization


def _render_active_job(project_id: str):
    service = KnowledgeExtractionJobService()
    active_job = service.latest(active_only=True, project_id=project_id, source_section="slack")

    if active_job:
        st.info(t("background_processing"))
        render_job_status(active_job.id)
        return active_job

    latest_job = service.latest(active_only=False, project_id=project_id, source_section="slack")
    if latest_job and not is_job_result_dismissed(latest_job.id):
        render_job_status(latest_job.id)

    return None


def render_slack_tab(memory_repository: MemoryRepository):
    project_id = get_current_project_id()
    st.header(t("slack_analysis"))

    chunk_size = int(
        workspace_repository.get_settings(project_id).get("slack_messages_per_chunk", 12)
    )

    active_job = _render_active_job(project_id)
    if active_job:
        return

    auth_tab, text_tab = st.tabs([
        t("source_tab_authorization"),
        t("source_tab_text"),
    ])
    with auth_tab:
        with st.container(key="source_auth_panel_slack"):
            render_source_authorization("slack")

    with text_tab:
        slack_text = st.text_area(
            t("paste_slack"),
            height=300,
            placeholder="[10:01] Alice: We decided to use USDC as settlement currency.",
            key="slack_ingest_text",
        )
        if st.button(t("process_slack"), type="primary", key="process_slack_text_button"):
            if not slack_text.strip():
                st.warning(t("paste_slack_warning"))
            else:
                service = KnowledgeExtractionJobService()
                job = service.start(
                    process_slack_text_job,
                    text=slack_text,
                    chunk_size=chunk_size,
                    project_id=project_id,
                    metadata={
                        "source": "slack",
                        "project_id": project_id,
                        "notification_email": get_authenticated_email(),
                    },
                )
                st.session_state["latest_knowledge_extraction_job_id"] = job.id
                st.success(t("processing_started_email"))
                st.rerun()
