import streamlit as st

from jobs.extraction_tasks import process_confluence_article_job
from jobs.knowledge_extraction_service import KnowledgeExtractionJobService
from repositories.memory_repository import MemoryRepository
from ui.job_status import render_job_status
from ui_v2.state import get_current_project_id
from ui_v2.auth import get_authenticated_email
from ui_v2.i18n import t


def _render_active_job(project_id: str):
    service = KnowledgeExtractionJobService()
    active_job = service.latest(active_only=True, project_id=project_id)

    if active_job:
        st.info(t("background_processing"))
        render_job_status(active_job.id)
        return active_job

    latest_job = service.latest(active_only=False, project_id=project_id)
    if latest_job:
        render_job_status(latest_job.id)

    return None


def render_confluence_tab(memory_repository: MemoryRepository):
    project_id = get_current_project_id()
    st.header(t("confluence_articles"))
    st.caption(t("confluence_caption"))

    article_title = st.text_input(t("article_title"), placeholder="Wallet Service Overview", key="confluence_ingest_article_title")
    confluence_text = st.text_area(
        t("paste_confluence"),
        height=350,
        placeholder="Paste article content, tables copied as text, requirements, decision logs, or architecture pages...",
        key="confluence_ingest_article_text",
    )

    active_job = _render_active_job(project_id)
    if active_job:
        return

    if st.button(t("process_confluence"), key="process_confluence_article_button", type="primary"):
        if not confluence_text.strip():
            st.warning(t("paste_confluence_warning"))
            return

        title = article_title.strip() or "Confluence article"
        service = KnowledgeExtractionJobService()
        job = service.start(
            process_confluence_article_job,
            text=confluence_text,
            title=title,
            project_id=project_id,
            metadata={
                "source": "confluence",
                "title": title,
                "project_id": project_id,
                "notification_email": get_authenticated_email(),
            },
        )

        st.session_state["latest_knowledge_extraction_job_id"] = job.id
        st.success(t("processing_started_email"))
        st.rerun()
