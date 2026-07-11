from pathlib import Path
import tempfile

import streamlit as st

from jobs.extraction_tasks import process_jira_pdfs_job, process_jira_text_job
from jobs.knowledge_extraction_service import KnowledgeExtractionJobService
from repositories.memory_repository import MemoryRepository
from ui.job_status import render_job_status


def _stage_uploaded_files(uploaded_files, prefix: str) -> list[dict[str, str]]:
    staged_dir = Path(tempfile.mkdtemp(prefix=prefix))
    specs = []

    for uploaded_file in uploaded_files:
        safe_name = (uploaded_file.name or "uploaded_file").replace("/", "_").replace("\\", "_")
        path = staged_dir / safe_name
        path.write_bytes(uploaded_file.getbuffer())
        specs.append({"name": safe_name, "path": str(path)})

    return specs


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


def render_jira_tab(memory_repository: MemoryRepository):
    st.header("Jira analysis")

    jira_text = st.text_area("Paste Jira tasks / epics / requirements", height=250)

    active_job = _render_active_job()
    if active_job:
        return

    if st.button("Process Jira text"):
        if not jira_text.strip():
            st.warning("Paste Jira text first.")
        else:
            service = KnowledgeExtractionJobService()
            job = service.start(process_jira_text_job, text=jira_text, metadata={"source": "jira_text"})
            st.session_state["latest_knowledge_extraction_job_id"] = job.id
            st.success("Jira text processing started in background.")
            st.rerun()

    st.divider()

    jira_pdfs = st.file_uploader("Upload Jira PDF exports", type=["pdf"], accept_multiple_files=True)

    if st.button("Process Jira PDFs"):
        if not jira_pdfs:
            st.warning("Upload at least one Jira PDF.")
            return

        file_specs = _stage_uploaded_files(jira_pdfs, prefix="project_brain_jira_pdf_stage_")
        service = KnowledgeExtractionJobService()
        job = service.start(
            process_jira_pdfs_job,
            file_specs=file_specs,
            metadata={"source": "jira_pdf", "files": [spec["name"] for spec in file_specs]},
        )

        st.session_state["latest_knowledge_extraction_job_id"] = job.id
        st.success("Jira PDF processing started in background.")
        st.rerun()
