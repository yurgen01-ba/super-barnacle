from pathlib import Path
import tempfile

import streamlit as st

from jobs.extraction_tasks import process_meeting_videos_job
from jobs.knowledge_extraction_service import KnowledgeExtractionJobService
from repositories.memory_repository import MemoryRepository
from repositories.workspace_repository import workspace_repository
from ui.job_status import render_job_status
from ui_v2.auth import get_authenticated_email
from ui_v2.state import get_current_project_id, set_current_page
from ui_v2.i18n import t


def _stage_uploaded_files(uploaded_files, prefix: str) -> list[dict[str, str]]:
    staged_dir = Path(tempfile.mkdtemp(prefix=prefix))
    specs = []
    for uploaded_file in uploaded_files:
        safe_name = (uploaded_file.name or "uploaded_file").replace("/", "_").replace("\\", "_")
        path = staged_dir / safe_name
        path.write_bytes(uploaded_file.getbuffer())
        specs.append({"name": safe_name, "path": str(path)})
    return specs


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


def _start_meeting_processing(uploaded_videos, settings: dict, project_id: str, participant_names: list[str]):
    file_specs = _stage_uploaded_files(
        uploaded_videos,
        prefix="project_brain_meeting_stage_",
    )
    segment_seconds = (
        int(settings["manual_segment_minutes"]) * 60
        if settings.get("manual_audio_segments")
        else None
    )
    runtime_settings = {
        "segment_seconds": segment_seconds,
        "language": settings.get("language"),
        "analyze_screen": bool(settings.get("analyze_screen")),
        "screen_interval_seconds": int(settings.get("screen_interval_seconds", 60)),
        "max_screen_frames": None,
        "screen_dedup_distance": int(settings.get("screen_dedup_distance", 8)),
        "vision_provider_name": "ollama",
        "vision_model": settings.get("vision_model"),
        "vision_host": settings.get("vision_host"),
        "vision_timeout_seconds": int(settings.get("vision_timeout_seconds", 180)),
        "transcript_extractor_provider": settings.get("transcript_extractor_provider"),
        "transcript_extractor_model": settings.get("transcript_extractor_model"),
        "transcript_extractor_host": settings.get("transcript_extractor_host"),
        "transcript_extractor_timeout_seconds": int(settings.get("transcript_extractor_timeout_seconds", 180)),
        "extract_canonical_facts": bool(settings.get("extract_canonical_facts")),
        "fact_extractor_model": settings.get("fact_extractor_model"),
        "fact_extractor_host": settings.get("fact_extractor_host"),
        "fact_extractor_timeout_seconds": int(settings.get("fact_extractor_timeout_seconds", 240)),
        "local_transcript_repair_enabled": bool(settings.get("local_transcript_repair_enabled", True)),
        "transcript_repair_min_bad_seconds": float(settings.get("transcript_repair_min_bad_seconds", 6.0)),
        "transcript_repair_min_quality_gain": float(settings.get("transcript_repair_min_quality_gain", 0.12)),
        "diarization_correction_enabled": bool(settings.get("diarization_correction_enabled", True)),
        "diarization_min_new_run_words": int(settings.get("diarization_min_new_run_words", 2)),
        "diarization_min_new_run_seconds": float(settings.get("diarization_min_new_run_seconds", 0.65)),
        "participant_names": participant_names,
        "vision_progress_callback": None,
        "audio_progress_callback": None,
        "fact_progress_callback": None,
        "screen_items_callback": None,
    }
    service = KnowledgeExtractionJobService()
    job = service.start(
        process_meeting_videos_job,
        file_specs=file_specs,
        settings=runtime_settings,
        project_id=project_id,
        metadata={
            "source": "meetings",
            "project_id": project_id,
            "files": [spec["name"] for spec in file_specs],
            "participants": participant_names,
            "notification_email": get_authenticated_email(),
        },
    )
    st.session_state["latest_knowledge_extraction_job_id"] = job.id
    workspace_repository.log_event(
        project_id,
        "extraction",
        "Запущена обработка видео",
        {
            "job_id": job.id,
            "files": [spec["name"] for spec in file_specs],
            "participants": participant_names,
        },
    )


def _participant_dialog(uploaded_videos, settings: dict, project_id: str):
    @st.dialog(t("conversation_participants"))
    def dialog_content():
        st.caption(t("participants_dialog_caption"))
        count = st.number_input(t("participant_count"), min_value=1, max_value=10, value=2, step=1)
        names = [
            st.text_input(f"SPEAKER_{index:02d}", key=f"meeting_participant_{index}")
            for index in range(int(count))
        ]
        if st.button(t("start_transcription"), type="primary", width="stretch"):
            clean_names = [" ".join(name.split()) for name in names]
            if any(not name for name in clean_names):
                st.error(t("fill_participants"))
                return
            _start_meeting_processing(uploaded_videos, settings, project_id, clean_names)
            st.success(t("processing_started_email"))
            st.rerun()
    dialog_content()


def render_meetings_tab(memory_repository: MemoryRepository):
    project_id = get_current_project_id()
    settings = workspace_repository.get_settings(project_id)

    st.header(t("meeting_analysis"))
    st.caption(t("meeting_caption"))

    uploaded_videos = st.file_uploader(
        t("upload_videos"),
        type=["mp4", "mov", "mkv"],
        accept_multiple_files=True,
    )

    with st.expander(t("applied_settings"), expanded=False):
        st.write({
            "language": settings.get("language") or "auto",
            "canonical_facts": settings.get("extract_canonical_facts"),
            "text_provider": settings.get("transcript_extractor_provider"),
            "text_model": settings.get("transcript_extractor_model"),
            "screen_analysis": settings.get("analyze_screen"),
            "screen_interval_seconds": settings.get("screen_interval_seconds"),
            "max_extracted_frames": "автоматически по длительности видео, не более 30",
        })
        if st.button(t("open_settings"), key="meetings_open_settings"):
            set_current_page("settings")
            st.rerun()

    active_job = _render_active_job(project_id)
    if active_job:
        return

    if st.button(t("process_video"), type="primary"):
        if not uploaded_videos:
            st.warning(t("choose_video_warning"))
            return
        _participant_dialog(uploaded_videos, settings, project_id)
