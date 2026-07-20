import streamlit as st

from jobs.extraction_tasks import process_confluence_article_job
from jobs.knowledge_extraction_service import KnowledgeExtractionJobService
from repositories.memory_repository import MemoryRepository
from ui.job_status import render_job_status
from ui_v2.state import get_current_project_id


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


def render_confluence_tab(memory_repository: MemoryRepository):
    project_id = get_current_project_id()
    st.header("Confluence Articles")
    st.caption("Paste Confluence article text or exported page text and extract Project Memory items.")

    article_title = st.text_input("Article title", placeholder="Example: Wallet Service Overview", key="confluence_ingest_article_title")
    confluence_text = st.text_area(
        "Paste Confluence article text",
        height=350,
        placeholder="Paste article content, tables copied as text, requirements, decision logs, or architecture pages...",
        key="confluence_ingest_article_text",
    )

    active_job = _render_active_job(project_id)
    if active_job:
        return

    if st.button("Process Confluence article", key="process_confluence_article_button", type="primary"):
        if not confluence_text.strip():
            st.warning("Paste Confluence article text first.")
            return

        title = article_title.strip() or "Confluence article"
        service = KnowledgeExtractionJobService()
        job = service.start(
            process_confluence_article_job,
            text=confluence_text,
            title=title,
            project_id=project_id,
            metadata={"source": "confluence", "title": title, "project_id": project_id},
        )

        st.session_state["latest_knowledge_extraction_job_id"] = job.id
        st.success("Confluence processing started in background.")
        st.rerun()
