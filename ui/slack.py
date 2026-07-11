import streamlit as st

from jobs.extraction_tasks import process_slack_text_job
from jobs.knowledge_extraction_service import KnowledgeExtractionJobService
from repositories.memory_repository import MemoryRepository
from ui.job_status import render_job_status


def _render_active_job():
    service = KnowledgeExtractionJobService()
    active_job = service.latest(active_only=True)

    if active_job:
        st.info("Knowledge extraction is running in background. You can switch tabs and return later.")
        render_job_status(active_job.id)
        return active_job

    latest_job = service.latest(active_only=False)
    if latest_job:
        render_job_status(latest_job.id)

    return None


def render_slack_tab(memory_repository: MemoryRepository):
    st.header("Slack paste analysis")

    slack_text = st.text_area(
        "Paste Slack messages",
        height=300,
        placeholder="[10:01] Alice: We decided to use USDC as settlement currency.",
    )

    chunk_size = st.slider("Slack messages per chunk", 5, 30, 12, 1)

    active_job = _render_active_job()
    if active_job:
        return

    if st.button("Process Slack text"):
        if not slack_text.strip():
            st.warning("Paste Slack messages first.")
            return

        service = KnowledgeExtractionJobService()
        job = service.start(
            process_slack_text_job,
            text=slack_text,
            chunk_size=chunk_size,
            metadata={"source": "slack"},
        )

        st.session_state["latest_knowledge_extraction_job_id"] = job.id
        st.success("Slack processing started in background.")
        st.rerun()
