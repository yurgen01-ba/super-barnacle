import streamlit as st

from jobs.extraction_tasks import process_jira_pdfs_job, process_jira_text_job
from jobs.knowledge_extraction_service import KnowledgeExtractionJobService
from repositories.memory_repository import MemoryRepository
from services.jira_archive_service import MAX_JIRA_PDFS, stage_jira_uploads
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


def render_jira_tab(memory_repository: MemoryRepository):
    project_id = get_current_project_id()
    st.header("Jira analysis")

    jira_text = st.text_area("Paste Jira tasks / epics / requirements", height=250)

    active_job = _render_active_job(project_id)
    if active_job:
        return

    if st.button("Process Jira text", type="primary"):
        if not jira_text.strip():
            st.warning("Paste Jira text first.")
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
            st.success("Обработка Jira запущена. Окно можно закрыть — после завершения придёт письмо.")
            st.rerun()

    st.markdown('<div class="pb-compact-divider"></div>', unsafe_allow_html=True)

    jira_pdfs = st.file_uploader(
        f"Загрузите Jira PDF или архив ZIP/7z — до {MAX_JIRA_PDFS} PDF-файлов",
        type=["pdf", "zip", "7z"],
        accept_multiple_files=True,
        help=(
            "Можно выбрать отдельные PDF либо архив ZIP/7z. "
            f"За один запуск обрабатывается не более {MAX_JIRA_PDFS} PDF-файлов."
        ),
    )
    st.caption("Поддерживаются PDF, ZIP и 7z. В архивах учитываются только PDF; максимум 20 файлов.")

    if st.button("Обработать Jira-файлы", type="primary"):
        if not jira_pdfs:
            st.warning("Загрузите хотя бы один PDF или архив ZIP/7z.")
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
        st.success(
            f"Обработка {len(file_specs)} Jira PDF запущена. "
            "Окно можно закрыть — после завершения придёт письмо."
        )
        st.rerun()
