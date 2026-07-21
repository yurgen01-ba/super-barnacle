import streamlit as st

from jobs.extraction_tasks import process_jira_pdfs_job, process_jira_text_job
from jobs.knowledge_extraction_service import KnowledgeExtractionJobService
from repositories.memory_repository import MemoryRepository
from services.jira_archive_service import MAX_JIRA_PDFS, stage_jira_uploads
from ui.job_status import render_job_status
from ui_v2.state import get_current_project_id
from ui_v2.auth import get_authenticated_email
from ui_v2.i18n import t
from ui_v2.browser_connectors import (
    render_atlassian_oauth_source_connector,
    render_local_browser_connector,
)

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


def render_jira_tab(memory_repository: MemoryRepository):
    project_id = get_current_project_id()
    st.header(t("jira_analysis"))

    render_atlassian_oauth_source_connector("jira")
    st.markdown('<div class="pb-compact-divider"></div>', unsafe_allow_html=True)
    render_local_browser_connector("atlassian", atlassian_products=("jira",))
    st.markdown('<div class="pb-compact-divider"></div>', unsafe_allow_html=True)

    jira_text = st.text_area(t("paste_jira"), height=250)

    active_job = _render_active_job(project_id)
    if active_job:
        return

    if st.button(t("process_jira"), type="primary"):
        if not jira_text.strip():
            st.warning(t("paste_jira_warning"))
        else:
            service = KnowledgeExtractionJobService()
            job = service.start(
                process_jira_text_job,
                text=jira_text,
                project_id=project_id,
                metadata={
                    "source": "jira_text",
                    "project_id": project_id,
                    "notification_email": get_authenticated_email(),
                },
            )
            st.session_state["latest_knowledge_extraction_job_id"] = job.id
            st.success(t("processing_started_email"))
            st.rerun()

    st.markdown('<div class="pb-compact-divider"></div>', unsafe_allow_html=True)

    jira_pdfs = st.file_uploader(
        t("jira_upload_label", count=MAX_JIRA_PDFS),
        type=["pdf", "zip", "7z"],
        accept_multiple_files=True,
        help=(
            "Можно выбрать отдельные PDF либо архив ZIP/7z. "
            f"За один запуск обрабатывается не более {MAX_JIRA_PDFS} PDF-файлов."
        ),
    )
    st.caption(t("jira_upload_caption"))

    if st.button(t("process_jira_files"), type="primary"):
        if not jira_pdfs:
            st.warning(t("choose_jira_warning"))
            return

        try:
            file_specs = stage_jira_uploads(jira_pdfs)
        except ValueError as exc:
            st.error(str(exc))
            return
        service = KnowledgeExtractionJobService()
        job = service.start(
            process_jira_pdfs_job,
            file_specs=file_specs,
            project_id=project_id,
            metadata={
                "source": "jira_pdf",
                "project_id": project_id,
                "files": [spec["name"] for spec in file_specs],
                "notification_email": get_authenticated_email(),
            },
        )

        st.session_state["latest_knowledge_extraction_job_id"] = job.id
        st.success(t("processing_started_email"))
        st.rerun()
