from __future__ import annotations

import streamlit as st

from providers.text.health import check_ollama_text_model
from providers.vision.health import check_ollama_health
from repositories.workspace_repository import workspace_repository
from ui_v2.components.html import title
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
    project_id = get_current_project_id()
    project = workspace_repository.get_project(project_id)
    settings = workspace_repository.get_settings(project_id)

    title("Настройки", "Все параметры обработки источников текущего проекта")

    with st.form("project_identity_settings"):
        project_name = st.text_input("Название проекта", value=project["name"])
        if st.form_submit_button("Сохранить название"):
            workspace_repository.rename_project(project_id, project_name)
            st.success("Название проекта сохранено")
            st.rerun()

    st.divider()
    st.subheader("Расшифровка встреч")
    st.caption(
        "Эти параметры применяются ко всем новым видео. Количество кадров экрана "
        "вычисляется автоматически: один кадр на заданный интервал, максимум 30."
    )

    language_values = list(LANGUAGES.values())
    language_labels = list(LANGUAGES.keys())

    with st.form("meeting_processing_settings"):
        language_label = st.selectbox(
            "Язык транскрибации",
            language_labels,
            index=_index(language_values, settings.get("language")),
        )

        st.markdown("#### Извлечение знаний из транскрипта")
        extract_canonical_facts = st.checkbox(
            "Извлекать и сохранять канонические факты",
            value=bool(settings.get("extract_canonical_facts", True)),
        )
        fact_extractor_model = st.selectbox(
            "Модель извлечения фактов",
            TEXT_MODELS,
            index=_index(TEXT_MODELS, settings.get("fact_extractor_model")),
        )
        fact_extractor_host = st.text_input(
            "Ollama host для фактов",
            value=settings.get("fact_extractor_host", "http://localhost:11434"),
        )
        fact_extractor_timeout_seconds = st.slider(
            "Таймаут извлечения фактов на блок, секунд",
            60,
            600,
            int(settings.get("fact_extractor_timeout_seconds", 240)),
            30,
        )

        transcript_extractor_provider = st.selectbox(
            "Провайдер извлечения знаний",
            ["ollama", "claude"],
            index=_index(["ollama", "claude"], settings.get("transcript_extractor_provider")),
        )
        transcript_extractor_model = st.selectbox(
            "Локальная текстовая модель",
            TEXT_MODELS,
            index=_index(TEXT_MODELS, settings.get("transcript_extractor_model")),
        )
        transcript_extractor_host = st.text_input(
            "Ollama host для текста",
            value=settings.get("transcript_extractor_host", "http://localhost:11434"),
        )
        transcript_extractor_timeout_seconds = st.slider(
            "Таймаут обработки текста на блок, секунд",
            60,
            420,
            int(settings.get("transcript_extractor_timeout_seconds", 180)),
            30,
        )

        st.markdown("#### Аудиосегменты")
        manual_audio_segments = st.checkbox(
            "Задавать размер аудиосегмента вручную",
            value=bool(settings.get("manual_audio_segments", False)),
        )
        manual_segment_minutes = st.slider(
            "Размер аудиосегмента, минут",
            5,
            60,
            int(settings.get("manual_segment_minutes", 20)),
            5,
            disabled=not manual_audio_segments,
        )

        st.markdown("#### Анализ экрана")
        analyze_screen = st.checkbox(
            "Анализировать содержимое экрана локальной vision-моделью",
            value=bool(settings.get("analyze_screen", False)),
        )
        screen_interval_seconds = st.slider(
            "Интервал между кадрами, секунд",
            30,
            180,
            int(settings.get("screen_interval_seconds", 60)),
            30,
        )
        screen_dedup_distance = st.slider(
            "Сила удаления похожих кадров",
            0,
            20,
            int(settings.get("screen_dedup_distance", 8)),
            1,
        )
        vision_model = st.selectbox(
            "Vision-модель",
            VISION_MODELS,
            index=_index(VISION_MODELS, settings.get("vision_model"), 1),
        )
        vision_host = st.text_input(
            "Ollama host для vision",
            value=settings.get("vision_host", "http://localhost:11434"),
        )
        vision_timeout_seconds = st.slider(
            "Таймаут на кадр, секунд",
            30,
            300,
            int(settings.get("vision_timeout_seconds", 180)),
            30,
        )

        submitted = st.form_submit_button("Сохранить настройки", type="primary")

    if submitted:
        workspace_repository.save_settings(project_id, {
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
        st.success("Настройки сохранены и будут применены к следующей загрузке")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Проверить текстовую модель"):
            st.write(check_ollama_text_model(
                host=settings.get("transcript_extractor_host"),
                model=settings.get("transcript_extractor_model"),
            ))
    with col2:
        if st.button("Проверить vision-модель"):
            st.write(check_ollama_health(
                host=settings.get("vision_host"),
                model=settings.get("vision_model"),
            ))
