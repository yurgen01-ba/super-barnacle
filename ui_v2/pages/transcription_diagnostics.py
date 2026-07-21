from __future__ import annotations

import json
import streamlit as st

from config import AUDIO_TRANSCRIPTION_BACKEND,WHISPERX_MODEL_NAME,WHISPERX_DEVICE,WHISPERX_COMPUTE_TYPE,WHISPERX_BATCH_SIZE,WHISPERX_ENABLE_ALIGNMENT,WHISPERX_ENABLE_DIARIZATION
from transcription.model_diagnostics import get_transcription_model_diagnostics

from repositories.artifact_repository import artifact_repository
from repositories.extraction_repository import extraction_repository
from ui_v2.i18n import t
from ui_v2.state import get_current_project_id


def render_transcription_diagnostics(project_id: str | None = None):
    project_id = project_id or get_current_project_id()
    st.subheader("Audio Intelligence Backend")
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Backend",AUDIO_TRANSCRIPTION_BACKEND)
    c2.metric("Model",WHISPERX_MODEL_NAME)
    c3.metric("Device",WHISPERX_DEVICE)
    c4.metric("Compute",WHISPERX_COMPUTE_TYPE)
    st.caption(f"Batch size: {WHISPERX_BATCH_SIZE} · Alignment: {WHISPERX_ENABLE_ALIGNMENT} · Diarization: {WHISPERX_ENABLE_DIARIZATION}")

    st.title(t("transcription_quality"))
    st.caption(t("diagnostics_caption"))

    model_diagnostics = get_transcription_model_diagnostics()
    if model_diagnostics.get("warning"):
        st.warning(model_diagnostics["warning"])
    with st.expander("Whisper model diagnostics", expanded=False):
        st.json(model_diagnostics)

    extractions = extraction_repository.list(project_id=project_id, limit=100)
    if not extractions:
        st.info(t("no_extractions"))
        return

    extraction = st.selectbox(
        t("extraction"),
        extractions,
        format_func=lambda item: f"{item['source_name']} · {item['status']} · {item['started_at']}",
    )

    artifacts = artifact_repository.list_by_extraction(extraction["id"])
    quality_artifacts = [a for a in artifacts if a["artifact_type"] == "transcript_quality"]
    transcript_artifacts = [a for a in artifacts if a["artifact_type"] in {"transcript", "clean_transcript", "repaired_transcript"}]

    st.subheader(t("quality"))
    if not quality_artifacts:
        st.warning(t("no_quality_artifacts"))
    else:
        for artifact in quality_artifacts:
            with st.expander(artifact["title"], expanded=False):
                try:
                    st.json(json.loads(artifact.get("content") or "{}"))
                except Exception:
                    st.text(artifact.get("content") or "")

    st.subheader(t("transcripts"))
    for artifact in transcript_artifacts:
        with st.expander(artifact["title"], expanded=False):
            query = st.text_input(t("search"), key=f"transcription_diag_search_{artifact['id']}")
            content = artifact.get("content") or ""
            if query:
                content = "\n".join(line for line in content.splitlines() if query.lower() in line.lower())
            st.text_area(t("content"), content, height=420, key=f"transcription_diag_{artifact['id']}")
