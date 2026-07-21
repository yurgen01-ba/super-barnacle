import base64
import html
from pathlib import Path
from uuid import uuid4

import streamlit as st
import streamlit.components.v1 as components

from jobs.extraction_tasks import process_meeting_videos_job
from jobs.knowledge_extraction_service import KnowledgeExtractionJobService
from repositories.memory_repository import MemoryRepository
from repositories.participant_repository import participant_repository
from repositories.workspace_repository import workspace_repository
from ui.job_status import render_job_status
from ui_v2.auth import get_authenticated_email
from ui_v2.state import get_current_project_id, set_current_page
from ui_v2.i18n import t


def _stage_uploaded_files(uploaded_files, prefix: str) -> list[dict[str, str]]:
    staged_root = Path("data") / "job_uploads"
    staged_dir = staged_root / f"{prefix}{uuid4().hex}"
    staged_dir.mkdir(parents=True, exist_ok=False)
    specs = []
    for uploaded_file in uploaded_files:
        safe_name = (uploaded_file.name or "uploaded_file").replace("/", "_").replace("\\", "_")
        path = staged_dir / safe_name
        path.write_bytes(uploaded_file.getbuffer())
        specs.append({"name": safe_name, "path": str(path)})
    return specs


def _job_speaker_samples(job) -> list[dict]:
    samples = []
    for item in (job.result or {}).get("results", []):
        samples.extend(item.get("speaker_samples") or [])
    return samples


def _audio_sample(sample: dict, element_id: str) -> None:
    path = Path(str(sample.get("clip_path") or ""))
    if not path.is_file():
        st.caption(t("speaker_sample_unavailable"))
        return
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    play = html.escape(t("play"))
    stop = html.escape(t("stop"))
    components.html(
        f"""
        <style>
          body {{ margin:0; background:transparent; font-family:Inter,Arial,sans-serif; }}
          .controls {{ display:flex; gap:8px; align-items:center; }}
          button {{ border:1px solid #6b7280; border-radius:10px; padding:7px 14px;
                    background:transparent; color:#9ca3af; cursor:pointer; font-size:14px; }}
          button:hover {{ color:#ff4b4b; border-color:#ff4b4b; }}
        </style>
        <audio id="{element_id}" preload="metadata" src="data:audio/wav;base64,{encoded}"></audio>
        <div class="controls">
          <button onclick="document.getElementById('{element_id}').play()">▶ {play}</button>
          <button onclick="const a=document.getElementById('{element_id}');a.pause();a.currentTime=0">■ {stop}</button>
        </div>
        """,
        height=48,
    )


def _speaker_dialog(job, project_id: str) -> None:
    samples = _job_speaker_samples(job)
    saved = participant_repository.meeting_speaker_names(project_id)

    @st.dialog(t("conversation_participants"), width="large")
    def dialog_content():
        st.caption(t("participants_after_processing_caption"))
        values = []
        for index, sample in enumerate(samples):
            source_ref = str(sample.get("file_name") or "")
            speaker = str(sample.get("speaker") or f"SPEAKER_{index:02d}")
            st.markdown(f"**{html.escape(speaker)}** · {html.escape(source_ref)}")
            name_col, audio_col = st.columns([0.58, 0.42], vertical_alignment="center")
            with name_col:
                name = st.text_input(
                    t("participant_name"),
                    value=saved.get((source_ref, speaker), ""),
                    key=f"speaker_name_{job.id}_{index}",
                    label_visibility="collapsed",
                    placeholder=t("participant_name"),
                )
            with audio_col:
                _audio_sample(sample, f"speaker-audio-{job.id}-{index}")
            values.append((source_ref, speaker, name))
        if st.button(t("save_participant_names"), type="primary", width="stretch"):
            clean_values = [(source, speaker, " ".join(name.split())) for source, speaker, name in values]
            if any(not name for _, _, name in clean_values):
                st.error(t("fill_participants"))
                return
            for source_ref, speaker, name in clean_values:
                participant_repository.set_meeting_speaker_name(
                    project_id=project_id,
                    source_ref=source_ref,
                    speaker=speaker,
                    name=name,
                )
            job.metadata["participant_names_saved"] = True
            st.success(t("participant_names_saved"))
            st.rerun()

    dialog_content()


def _completed_speaker_controls(project_id: str):
    def render(job):
        samples = _job_speaker_samples(job)
        if not samples:
            return
        opened_key = f"speaker_dialog_opened_{job.id}"
        if st.button(t("edit_participant_names"), key=f"edit_speakers_{job.id}"):
            _speaker_dialog(job, project_id)
        elif not st.session_state.get(opened_key):
            st.session_state[opened_key] = True
            _speaker_dialog(job, project_id)
    return render


def _render_active_job(project_id: str):
    service = KnowledgeExtractionJobService()
    active_job = service.latest(active_only=True, project_id=project_id, source_section="meetings")
    if active_job:
        st.info(t("background_processing"))
        render_job_status(active_job.id, _completed_speaker_controls(project_id))
        return active_job
    latest_job = service.latest(active_only=False, project_id=project_id, source_section="meetings")
    if latest_job:
        render_job_status(latest_job.id, _completed_speaker_controls(project_id))
    return None


def _start_meeting_processing(uploaded_videos, settings: dict, project_id: str):
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
            "resume_kind": "meeting_videos",
            "file_specs": file_specs,
            "settings": runtime_settings,
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
        },
    )


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
        _start_meeting_processing(uploaded_videos, settings, project_id)
        st.success(t("processing_started_email"))
        st.rerun()
