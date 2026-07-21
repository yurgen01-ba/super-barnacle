from __future__ import annotations

import streamlit as st

from providers.text.health import check_ollama_text_model
from providers.vision.health import check_ollama_health
from repositories.workspace_repository import workspace_repository
from ui_v2.auth import get_authenticated_user
from ui_v2.components.html import title
from ui_v2.i18n import t
from ui_v2.state import get_current_project_id


LANGUAGES = {
    "Русский (рекомендуется)": "ru",
    "Автоопределение": None,
    "English": "en",
    "Українська": "uk",
    "Polski": "pl",
}
TEXT_MODELS = ["qwen2.5:7b", "qwen2.5:3b", "qwen2.5:14b"]
VISION_MODELS = ["qwen2.5vl:3b", "qwen2.5vl:7b", "qwen2.5vl"]


def _index(options: list, value, fallback: int = 0) -> int:
    try:
        return options.index(value)
    except ValueError:
        return fallback


def render_settings():
    user = get_authenticated_user() or {}
    project_id = get_current_project_id()
    project = workspace_repository.get_project(project_id, user["id"])
    settings = workspace_repository.get_settings(project_id)

    title(t("settings"), t("settings_caption"))

    if workspace_repository.is_owner(project_id, user["id"]):
        with st.form("project_identity_settings"):
            project_name = st.text_input(t("project_name"), value=project["name"])
            if st.form_submit_button(t("save_name")):
                workspace_repository.rename_project(project_id, project_name, user["id"])
                st.success(t("name_saved"))
                st.rerun()

    st.divider()
    st.subheader("Slack")
    st.caption(t("slack_settings_caption"))
    with st.form("slack_processing_settings"):
        slack_messages_per_chunk = st.slider(
            t("messages_per_chunk"),
            5,
            30,
            int(settings.get("slack_messages_per_chunk", 12)),
            1,
        )
        slack_submitted = st.form_submit_button(t("save_slack"), type="primary")

    if slack_submitted:
        workspace_repository.save_settings(
            project_id,
            {**settings, "slack_messages_per_chunk": slack_messages_per_chunk},
        )
        st.success(t("slack_saved"))

    st.divider()
    st.subheader(t("meeting_transcription"))
    st.caption(
        t("meeting_settings_caption")
    )

    language_values = list(LANGUAGES.values())
    language_labels = list(LANGUAGES.keys())

    with st.form("meeting_processing_settings"):
        language_label = st.selectbox(
            t("transcription_language"),
            language_labels,
            index=_index(language_values, settings.get("language")),
        )

        st.markdown(f"#### {t('knowledge_extraction')}")
        extract_canonical_facts = st.checkbox(
            t("extract_facts"),
            value=bool(settings.get("extract_canonical_facts", True)),
        )
        fact_extractor_model = st.selectbox(
            t("fact_model"),
            TEXT_MODELS,
            index=_index(TEXT_MODELS, settings.get("fact_extractor_model")),
        )
        fact_extractor_host = st.text_input(
            "Ollama host для фактов",
            value=settings.get("fact_extractor_host", "http://localhost:11434"),
        )
        fact_extractor_timeout_seconds = st.slider(
            t("fact_timeout"),
            60,
            600,
            int(settings.get("fact_extractor_timeout_seconds", 240)),
            30,
        )

        transcript_extractor_provider = st.selectbox(
            t("knowledge_provider"),
            ["ollama", "claude"],
            index=_index(["ollama", "claude"], settings.get("transcript_extractor_provider")),
        )
        transcript_extractor_model = st.selectbox(
            t("local_text_model"),
            TEXT_MODELS,
            index=_index(TEXT_MODELS, settings.get("transcript_extractor_model")),
        )
        transcript_extractor_host = st.text_input(
            "Ollama host для текста",
            value=settings.get("transcript_extractor_host", "http://localhost:11434"),
        )
        transcript_extractor_timeout_seconds = st.slider(
            t("text_timeout"),
            60,
            420,
            int(settings.get("transcript_extractor_timeout_seconds", 180)),
            30,
        )

        st.markdown(f"#### {t('audio_segments')}")
        manual_audio_segments = st.checkbox(
            t("manual_segments"),
            value=bool(settings.get("manual_audio_segments", False)),
        )
        manual_segment_minutes = st.slider(
            t("segment_minutes"),
            5,
            60,
            int(settings.get("manual_segment_minutes", 20)),
            5,
            disabled=not manual_audio_segments,
        )

        st.markdown(f"#### {t('screen_analysis')}")
        analyze_screen = st.checkbox(
            t("analyze_screen"),
            value=bool(settings.get("analyze_screen", False)),
        )
        screen_interval_seconds = st.slider(
            t("frame_interval"),
            30,
            180,
            int(settings.get("screen_interval_seconds", 60)),
            30,
        )
        screen_dedup_distance = st.slider(
            t("dedup_strength"),
            0,
            20,
            int(settings.get("screen_dedup_distance", 8)),
            1,
        )
        vision_model = st.selectbox(
            t("vision_model"),
            VISION_MODELS,
            index=_index(VISION_MODELS, settings.get("vision_model"), 1),
        )
        vision_host = st.text_input(
            "Ollama host для vision",
            value=settings.get("vision_host", "http://localhost:11434"),
        )
        vision_timeout_seconds = st.slider(
            t("frame_timeout"),
            30,
            300,
            int(settings.get("vision_timeout_seconds", 180)),
            30,
        )

        submitted = st.form_submit_button(t("save_settings"), type="primary")

    if submitted:
        workspace_repository.save_settings(project_id, {
            "slack_messages_per_chunk": settings.get("slack_messages_per_chunk", 12),
            "language": LANGUAGES[language_label],
            "extract_canonical_facts": extract_canonical_facts,
            "fact_extractor_model": fact_extractor_model,
            "fact_extractor_host": fact_extractor_host,
            "fact_extractor_timeout_seconds": fact_extractor_timeout_seconds,
            "transcript_extractor_provider": transcript_extractor_provider,
            "transcript_extractor_model": transcript_extractor_model,
            "transcript_extractor_host": transcript_extractor_host,
            "transcript_extractor_timeout_seconds": transcript_extractor_timeout_seconds,
            "manual_audio_segments": manual_audio_segments,
            "manual_segment_minutes": manual_segment_minutes,
            "analyze_screen": analyze_screen,
            "screen_interval_seconds": screen_interval_seconds,
            "screen_dedup_distance": screen_dedup_distance,
            "vision_model": vision_model,
            "vision_host": vision_host,
            "vision_timeout_seconds": vision_timeout_seconds,
        })
        st.success(t("settings_saved"))

    col1, col2 = st.columns(2)
    with col1:
        if st.button(t("check_text_model")):
            st.write(check_ollama_text_model(
                host=settings.get("transcript_extractor_host"),
                model=settings.get("transcript_extractor_model"),
            ))
    with col2:
        if st.button(t("check_vision_model")):
            st.write(check_ollama_health(
                host=settings.get("vision_host"),
                model=settings.get("vision_model"),
            ))
