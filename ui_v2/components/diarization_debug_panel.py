from __future__ import annotations

import streamlit as st


def render_diarization_debug_panel(
    audio_intelligence: dict | None,
) -> None:
    payload = audio_intelligence or {}
    runtime = payload.get("runtime") or {}
    debug = runtime.get("diarization_debug") or {}
    warnings = payload.get("warnings") or []

    st.subheader("Diarization Deep Diagnostics")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Token",
        "Found" if debug.get("token_found") else "Missing",
    )
    col2.metric(
        "Diarization",
        "Completed" if debug.get("completed") else "Not completed",
    )
    col3.metric(
        "Turns",
        int(debug.get("diarization_turns") or 0),
    )
    col4.metric(
        "Speakers",
        len(debug.get("assigned_speaker_labels") or []),
    )

    failure_message = debug.get("failure_message")
    if failure_message:
        st.error(
            f"{debug.get('failure_type')}: {failure_message}"
        )

    for warning in warnings:
        st.warning(str(warning))

    stages = debug.get("stages") or []
    if stages:
        st.dataframe(stages, use_container_width=True)

    with st.expander("Full diarization debug report", expanded=False):
        st.json(debug)

    traceback_text = debug.get("failure_traceback")
    if traceback_text:
        with st.expander("Failure traceback", expanded=False):
            st.code(traceback_text, language="text")
