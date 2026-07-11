import streamlit as st

from jobs.extraction_tasks import process_confluence_article_job
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


def render_confluence_tab(memory_repository: MemoryRepository):
    st.header("Confluence Articles")
    st.caption("Paste Confluence article text or exported page text and extract Project Memory items.")

    article_title = st.text_input("Article title", placeholder="Example: Wallet Service Overview", key="confluence_ingest_article_title")
    confluence_text = st.text_area(
        "Paste Confluence article text",
        height=350,
        placeholder="Paste article content, tables copied as text, requirements, decision logs, or architecture pages...",
        key="confluence_ingest_article_text",
    )

    active_job = _render_active_job()
    if active_job:
        return

    if st.button("Process Confluence article", key="process_confluence_article_button"):
        if not confluence_text.strip():
            st.warning("Paste Confluence article text first.")
            return

        title = article_title.strip() or "Confluence article"
        service = KnowledgeExtractionJobService()
        job = service.start(
            process_confluence_article_job,
            text=confluence_text,
            title=title,
            metadata={"source": "confluence", "title": title},
        )

        st.session_state["latest_knowledge_extraction_job_id"] = job.id
        st.success("Confluence processing started in background.")
        st.rerun()
