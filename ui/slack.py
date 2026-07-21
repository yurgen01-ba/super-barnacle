import streamlit as st

from jobs.extraction_tasks import process_slack_text_job
from jobs.knowledge_extraction_service import KnowledgeExtractionJobService
from repositories.memory_repository import MemoryRepository
from repositories.workspace_repository import workspace_repository
from ui.job_status import render_job_status
from ui_v2.state import get_current_project_id
from ui_v2.auth import get_authenticated_email


def _render_active_job(project_id: str):
    service = KnowledgeExtractionJobService()
    active_job = service.latest(active_only=True, project_id=project_id)

    if active_job:
        st.info("Knowledge extraction is running in background. You can switch tabs and return later.")
        render_job_status(active_job.id)
        return active_job

    latest_job = service.latest(active_only=False, project_id=project_id)
    if latest_job:
        render_job_status(latest_job.id)

    return None


def render_slack_tab(memory_repository: MemoryRepository):
    project_id = get_current_project_id()

    slack_text = st.text_area(
        "Paste Slack messages",
        height=300,
        placeholder="[10:01] Alice: We decided to use USDC as settlement currency.",
    )

    chunk_size = int(
        workspace_repository.get_settings(project_id).get("slack_messages_per_chunk", 12)
    )

    active_job = _render_active_job(project_id)
    if active_job:
        return

    if st.button("Process Slack text", type="primary"):
        if not slack_text.strip():
            st.warning("Paste Slack messages first.")
            return

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
        st.success("Обработка Slack запущена. Окно можно закрыть — после завершения придёт письмо.")
        st.rerun()
