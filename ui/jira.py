import streamlit as st

from jobs.extraction_tasks import process_jira_pdfs_job, process_jira_text_job
from jobs.knowledge_extraction_service import KnowledgeExtractionJobService
from repositories.memory_repository import MemoryRepository
from services.jira_archive_service import MAX_JIRA_PDFS, stage_jira_uploads
from ui.job_status import render_job_status
from ui_v2.state import get_current_project_id
from ui_v2.auth import get_authenticated_email
from ui_v2.i18n import t
from ui_v2.source_connections import render_source_authorization

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

    active_job = _render_active_job(project_id)
    if active_job:
        return

    auth_tab, files_tab, text_tab = st.tabs([
        t("source_tab_authorization"),
        t("source_tab_files"),
        t("source_tab_text"),
    ])

    with auth_tab:
        with st.container(key="source_auth_panel_jira"):
            render_source_authorization("jira")

    with files_tab:
        jira_pdfs = st.file_uploader(
            t("jira_upload_label", count=MAX_JIRA_PDFS),
            type=["pdf", "zip", "7z"],
            accept_multiple_files=True,
            help=(
                "Можно выбрать отдельные PDF либо архив ZIP/7z. "
                f"За один запуск обрабатывается не более {MAX_JIRA_PDFS} PDF-файлов."
            ),
            key="jira_pdf_uploads",
        )
        st.caption(t("jira_upload_caption"))
        if st.button(t("process_jira_files"), type="primary", key="process_jira_files_button"):
            if not jira_pdfs:
                st.warning(t("choose_jira_warning"))
            else:
                try:
                    file_specs = stage_jira_uploads(jira_pdfs)
                except ValueError as exc:
                    st.error(str(exc))
                else:
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

    with text_tab:
        jira_text = st.text_area(t("paste_jira"), height=250, key="jira_ingest_text")
        if st.button(t("process_jira"), type="primary", key="process_jira_text_button"):
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
