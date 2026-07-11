from __future__ import annotations

import json
import streamlit as st

from config import AUDIO_TRANSCRIPTION_BACKEND,WHISPERX_MODEL_NAME,WHISPERX_DEVICE,WHISPERX_COMPUTE_TYPE,WHISPERX_BATCH_SIZE,WHISPERX_ENABLE_ALIGNMENT,WHISPERX_ENABLE_DIARIZATION
from transcription.model_diagnostics import get_transcription_model_diagnostics

from repositories.artifact_repository import artifact_repository
from repositories.extraction_repository import extraction_repository


def render_transcription_diagnostics(project_id: str = "default"):
    st.subheader("Audio Intelligence Backend")
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Backend",AUDIO_TRANSCRIPTION_BACKEND)
    c2.metric("Model",WHISPERX_MODEL_NAME)
    c3.metric("Device",WHISPERX_DEVICE)
    c4.metric("Compute",WHISPERX_COMPUTE_TYPE)
    st.caption(f"Batch size: {WHISPERX_BATCH_SIZE} · Alignment: {WHISPERX_ENABLE_ALIGNMENT} · Diarization: {WHISPERX_ENABLE_DIARIZATION}")

    st.title("Transcription Quality")
    st.caption("Inspect raw, clean and repaired transcript artifacts and segment quality.")

    model_diagnostics = get_transcription_model_diagnostics()
    if model_diagnostics.get("warning"):
        st.warning(model_diagnostics["warning"])
    with st.expander("Whisper model diagnostics", expanded=False):
        st.json(model_diagnostics)

    extractions = extraction_repository.list(project_id=project_id, limit=100)
    if not extractions:
        st.info("No extractions yet.")
        return

    extraction = st.selectbox(
        "Extraction",
        extractions,
        format_func=lambda item: f"{item['source_name']} · {item['status']} · {item['started_at']}",
    )

    artifacts = artifact_repository.list_by_extraction(extraction["id"])
    quality_artifacts = [a for a in artifacts if a["artifact_type"] == "transcript_quality"]
    transcript_artifacts = [a for a in artifacts if a["artifact_type"] in {"transcript", "clean_transcript", "repaired_transcript"}]

    st.subheader("Quality")
    if not quality_artifacts:
        st.warning("No transcript quality artifacts found.")
    else:
        for artifact in quality_artifacts:
            with st.expander(artifact["title"], expanded=False):
                try:
                    st.json(json.loads(artifact.get("content") or "{}"))
                except Exception:
                    st.text(artifact.get("content") or "")

    st.subheader("Transcripts")
    for artifact in transcript_artifacts:
        with st.expander(artifact["title"], expanded=False):
            query = st.text_input("Search", key=f"transcription_diag_search_{artifact['id']}")
            content = artifact.get("content") or ""
            if query:
                content = "\n".join(line for line in content.splitlines() if query.lower() in line.lower())
            st.text_area("Content", content, height=420, key=f"transcription_diag_{artifact['id']}")
