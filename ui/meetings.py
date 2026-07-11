from pathlib import Path
import tempfile

import streamlit as st

from jobs.extraction_tasks import process_meeting_videos_job
from jobs.knowledge_extraction_service import KnowledgeExtractionJobService
from providers.text.health import check_ollama_text_model
from providers.vision.health import check_ollama_health
from repositories.memory_repository import MemoryRepository
from ui.job_status import render_job_status


LANGUAGE_OPTIONS = {
    "Russian (recommended)": "ru",
    "Auto-detect per segment": None,
    "English": "en",
    "Russian": "ru",
    "Ukrainian": "uk",
    "Polish": "pl",
}


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


def render_meetings_tab(memory_repository: MemoryRepository):
    st.header("Meeting video analysis")

    uploaded_videos = st.file_uploader(
        "Upload one or more meeting videos",
        type=["mp4", "mov", "mkv"],
        accept_multiple_files=True,
    )

    selected_language_label = st.selectbox("Transcription language", options=list(LANGUAGE_OPTIONS.keys()), index=0, help="For Russian-language project meetings, forced Russian usually gives much better transcription than auto-detect.")
    language = LANGUAGE_OPTIONS[selected_language_label]

    st.subheader("Canonical Facts")
    extract_canonical_facts = st.checkbox(
        "Extract and save Canonical Facts",
        value=True,
        help="New Project Model foundation layer: subject → predicate → object.",
    )

    fact_extractor_model = "qwen2.5:7b"
    fact_extractor_host = "http://localhost:11434"
    fact_extractor_timeout_seconds = 240

    if extract_canonical_facts:
        col_f1, col_f2 = st.columns(2)

        with col_f1:
            fact_extractor_model = st.selectbox(
                "Fact extractor model",
                options=["qwen2.5:7b", "qwen2.5:3b", "qwen2.5:14b"],
                index=0,
                key="meetings_fact_extractor_model",
            )

        with col_f2:
            fact_extractor_timeout_seconds = st.slider(
                "Fact extraction timeout per chunk, seconds",
                60,
                600,
                240,
                30,
                key="meetings_fact_extractor_timeout",
            )

        fact_extractor_host = st.text_input(
            "Fact extractor Ollama host",
            value="http://localhost:11434",
            key="meetings_fact_extractor_host",
        )

        if st.button("Test fact extractor model", key="test_fact_extractor_model"):
            health = check_ollama_text_model(host=fact_extractor_host, model=fact_extractor_model)
            st.write(health)

    st.subheader("Transcript knowledge extraction")

    col_t1, col_t2 = st.columns(2)

    with col_t1:
        transcript_extractor_provider = st.selectbox(
            "Transcript extractor",
            options=["ollama", "claude"],
            index=0,
            help="Ollama is local/free. Claude is paid fallback.",
        )

    with col_t2:
        transcript_extractor_model = st.selectbox(
            "Local text model",
            options=["qwen2.5:7b", "qwen2.5:3b", "qwen2.5:14b"],
            index=0,
            disabled=transcript_extractor_provider != "ollama",
        )

    transcript_extractor_host = "http://localhost:11434"
    transcript_extractor_timeout_seconds = 180

    if transcript_extractor_provider == "ollama":
        col_t3, col_t4 = st.columns(2)

        with col_t3:
            transcript_extractor_host = st.text_input("Ollama text host", value="http://localhost:11434", key="meetings_text_ollama_host")

        with col_t4:
            transcript_extractor_timeout_seconds = st.slider("Text extraction timeout per chunk, seconds", 60, 420, 180, 30)

        if st.button("Test local text model", key="test_text_ollama_model"):
            health = check_ollama_text_model(host=transcript_extractor_host, model=transcript_extractor_model)
            st.write(health)

    with st.expander("Advanced audio settings", expanded=False):
        manual_audio_segments = st.checkbox("Override automatic audio segment size", value=False)
        manual_segment_minutes = st.slider("Manual audio segment size, minutes", 5, 60, 20, 5, disabled=not manual_audio_segments)

    st.divider()

    analyze_screen = st.checkbox("Analyze screen content safely with local Ollama/Qwen", value=False)

    screen_interval_seconds = 60
    max_screen_frames = 1
    screen_dedup_distance = 8
    vision_model = "qwen2.5vl:7b"
    vision_host = "http://localhost:11434"
    vision_timeout_seconds = 180

    if analyze_screen:
        col3, col4 = st.columns(2)

        with col3:
            screen_interval_seconds = st.slider("Screen frame interval, seconds", 30, 180, 60, 30)

        with col4:
            max_screen_frames = st.slider("Max extracted frames", 1, 30, 1, 1)

        col5, col6 = st.columns(2)

        with col5:
            screen_dedup_distance = st.slider("Frame deduplication strength", 0, 20, 8, 1)

        with col6:
            vision_model = st.selectbox("Vision model", options=["qwen2.5vl:3b", "qwen2.5vl:7b", "qwen2.5vl"], index=1)

        col7, col8 = st.columns(2)

        with col7:
            vision_timeout_seconds = st.slider("Timeout per frame, seconds", 30, 300, 180, 30)

        with col8:
            vision_host = st.text_input("Vision provider host", value="http://localhost:11434", key="meetings_vision_host")

        if st.button("Test Ollama vision connection", key="test_ollama_connection"):
            health = check_ollama_health(host=vision_host, model=vision_model)
            st.write(health)

    active_job = _render_active_job()
    if active_job:
        return

    if st.button("Process meeting videos"):
        if not uploaded_videos:
            st.warning("Upload at least one video.")
            return

        file_specs = _stage_uploaded_files(uploaded_videos, prefix="project_brain_meeting_stage_")
        segment_seconds = manual_segment_minutes * 60 if manual_audio_segments else None

        settings = {
            "segment_seconds": segment_seconds,
            "language": language,
            "analyze_screen": analyze_screen,
            "screen_interval_seconds": screen_interval_seconds,
            "max_screen_frames": max_screen_frames,
            "screen_dedup_distance": screen_dedup_distance,
            "vision_provider_name": "ollama",
            "vision_model": vision_model,
            "vision_host": vision_host,
            "vision_timeout_seconds": vision_timeout_seconds,
            "transcript_extractor_provider": transcript_extractor_provider,
            "transcript_extractor_model": transcript_extractor_model,
            "transcript_extractor_host": transcript_extractor_host,
            "transcript_extractor_timeout_seconds": transcript_extractor_timeout_seconds,
            "extract_canonical_facts": extract_canonical_facts,
            "fact_extractor_model": fact_extractor_model,
            "fact_extractor_host": fact_extractor_host,
            "fact_extractor_timeout_seconds": fact_extractor_timeout_seconds,
            "vision_progress_callback": None,
            "audio_progress_callback": None,
            "fact_progress_callback": None,
            "screen_items_callback": None,
        }

        service = KnowledgeExtractionJobService()
        job = service.start(
            process_meeting_videos_job,
            file_specs=file_specs,
            settings=settings,
            metadata={"source": "meetings", "files": [spec["name"] for spec in file_specs]},
        )

        st.session_state["latest_knowledge_extraction_job_id"] = job.id
        st.success("Meeting processing started in background.")
        st.rerun()
