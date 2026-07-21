from __future__ import annotations

from pathlib import Path
import tempfile

import streamlit as st

from jobs.extraction_tasks import process_files_job
from jobs.knowledge_extraction_service import KnowledgeExtractionJobService
from repositories.workspace_repository import workspace_repository
from ui.job_status import render_job_status
from ui_v2.auth import get_authenticated_email
from ui_v2.state import get_current_project_id


FILE_TYPES = ["txt", "md", "csv", "json", "log", "yaml", "yml", "pdf", "docx", "xlsx", "pptx"]


def _stage_files(uploaded_files) -> list[dict[str, str]]:
    directory = Path(tempfile.mkdtemp(prefix="project_brain_files_stage_"))
    result = []
    for uploaded in uploaded_files:
        name = (uploaded.name or "uploaded_file").replace("/", "_").replace("\\", "_")
        path = directory / name
        path.write_bytes(uploaded.getbuffer())
        result.append({"name": name, "path": str(path)})
    return result


def render_files_tab(memory_repository):
    project_id = get_current_project_id()
    service = KnowledgeExtractionJobService()

    st.header("Загрузка файлов")
    st.caption(
        "Поддерживаются текстовые документы, PDF, Word, Excel и PowerPoint. "
        "Извлечённый текст и структурированные знания сохраняются как артефакты проекта."
    )
    uploaded_files = st.file_uploader(
        "Выберите файлы",
        type=FILE_TYPES,
        accept_multiple_files=True,
        key="generic_project_files_uploader",
    )

    active_job = service.latest(active_only=True, project_id=project_id)
    if active_job:
        st.info("Файлы обрабатываются в фоне.")
        render_job_status(active_job.id)
        return

    latest_job = service.latest(active_only=False, project_id=project_id)
    if latest_job and (latest_job.metadata or {}).get("source") == "files":
        render_job_status(latest_job.id)

    if st.button("Обработать файлы", type="primary"):
        if not uploaded_files:
            st.warning("Сначала выберите хотя бы один файл.")
            return
        specs = _stage_files(uploaded_files)
        job = service.start(
            process_files_job,
            file_specs=specs,
            project_id=project_id,
            metadata={
                "source": "files",
                "project_id": project_id,
                "files": [item["name"] for item in specs],
                "notification_email": get_authenticated_email(),
            },
        )
        workspace_repository.log_event(
            project_id,
            "extraction",
            "Запущена обработка файлов",
            {"job_id": job.id, "files": [item["name"] for item in specs]},
        )
        st.session_state["latest_knowledge_extraction_job_id"] = job.id
        st.success("Обработка файлов запущена. Окно можно закрыть — после завершения придёт письмо.")
        st.rerun()
