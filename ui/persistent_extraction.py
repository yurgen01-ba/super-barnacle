from __future__ import annotations

import streamlit as st

from jobs.knowledge_extraction_service import KNOWLEDGE_EXTRACTION_JOB, KnowledgeExtractionJobService
from ui.job_status import render_job_status


def start_or_attach_knowledge_extraction(
    extraction_callable,
    *args,
    button_label: str = "Start knowledge extraction",
    metadata: dict | None = None,
    **kwargs,
):
    """
    Streamlit helper.

    Use this instead of calling extraction directly from a page render.
    The returned job continues running after tab/page changes.
    """
    service = KnowledgeExtractionJobService()

    active_job = service.latest(active_only=True)

    if active_job:
        st.info("Knowledge extraction is already running.")
        render_job_status(active_job.id)
        return active_job

    if st.button(button_label, type="primary"):
        job = service.start(
            extraction_callable,
            *args,
            metadata=metadata,
            **kwargs,
        )
        st.session_state["latest_knowledge_extraction_job_id"] = job.id
        st.rerun()

    latest_job_id = st.session_state.get("latest_knowledge_extraction_job_id")
    if latest_job_id:
        render_job_status(latest_job_id)

    return None


def render_knowledge_extraction_status():
    service = KnowledgeExtractionJobService()
    job = service.latest(active_only=False)

    if not job:
        st.info("No knowledge extraction jobs yet.")
        return

    render_job_status(job.id)
