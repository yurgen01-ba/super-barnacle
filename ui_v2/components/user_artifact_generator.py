from __future__ import annotations

import streamlit as st

from ai.graph_artifact_builder import GraphArtifactBuilder
from graph.graph_retriever_v2 import GraphRetrieverV2
from providers.text.factory import create_text_provider
from repositories.workspace_repository import workspace_repository
from services.user_artifact_service import save_user_generated_artifact
from ui_v2.i18n import t
from ui_v2.loaders import inline_seal_loader


ARTIFACT_PRESETS = {
    "project_report": (
        "Отчёт по проекту",
        "Создай структурированный отчёт по проекту: цели, участники, процессы, требования, решения, риски и открытые вопросы.",
    ),
    "pitch_deck": (
        "Pitch deck",
        "Создай готовую структуру pitch deck по слайдам: проблема, решение, пользователи, ценность, продукт, рынок, бизнес-модель, риски и следующие шаги.",
    ),
    "product_requirements": (
        "Требования к продукту",
        "Сформируй документ требований: контекст, цели, функциональные требования, бизнес-правила, ограничения, acceptance criteria и открытые вопросы.",
    ),
    "decision_log": (
        "Журнал решений",
        "Составь журнал подтверждённых решений с обоснованием, последствиями, источниками и нерешёнными вопросами.",
    ),
    "risk_register": (
        "Реестр рисков",
        "Составь реестр рисков: риск, вероятность, влияние, признаки, меры снижения и ответственный, если он известен.",
    ),
}

PRESET_TRANSLATION_KEYS = {
    key: (f"preset_{key}_title", f"preset_{key}_instruction")
    for key in ARTIFACT_PRESETS
}


def render_user_artifact_generator(
    *,
    project_id: str,
    artifact_type: str,
    default_title: str,
    default_instruction: str,
    key_prefix: str,
):
    st.markdown(f"#### {default_title}")
    title = st.text_input(
        t("result_name"),
        value=default_title,
        key=f"{key_prefix}_title",
    )
    instruction = st.text_area(
        t("ai_task"),
        value=default_instruction,
        height=150,
        key=f"{key_prefix}_instruction",
    )

    if not st.button(t("generate"), key=f"{key_prefix}_generate", type="primary", width="stretch"):
        return

    if not title.strip() or not instruction.strip():
        st.warning(t("artifact_fields_required"))
        return

    settings = workspace_repository.get_settings(project_id)
    provider_name = settings.get("transcript_extractor_provider", "ollama")
    if provider_name != "ollama":
        st.error(t("ollama_artifacts_only"))
        return

    try:
        with inline_seal_loader(t("artifact_generating")):
            provider = create_text_provider(
                provider_name="ollama",
                model=settings.get("transcript_extractor_model", "qwen2.5:7b"),
                host=settings.get("transcript_extractor_host", "http://localhost:11434"),
                timeout_seconds=settings.get("transcript_extractor_timeout_seconds", 180),
            )
            builder = GraphArtifactBuilder(GraphRetrieverV2(project_id=project_id))
            prompt = builder.build_prompt(artifact_type=artifact_type, instruction=instruction.strip())
            content = provider.generate(prompt).strip()
        if not content:
            raise RuntimeError("Локальная модель вернула пустой результат.")

        artifact = save_user_generated_artifact(
            project_id=project_id,
            artifact_type=artifact_type,
            title=title.strip(),
            content=content,
            description="AI-артефакт, созданный по запросу пользователя из Project Graph.",
            metadata={
                "instruction": instruction.strip(),
                "provider": "ollama",
                "model": settings.get("transcript_extractor_model", "qwen2.5:7b"),
            },
        )
        workspace_repository.log_event(
            project_id,
            "artifact",
            "AI-артефакт создан",
            {"artifact_id": artifact.id, "artifact_type": artifact_type, "title": title.strip()},
        )
        st.success(t("artifact_created"))
        st.markdown(content)
        st.download_button(
            t("download_markdown"),
            data=content,
            file_name=f"{artifact.id}.md",
            mime="text/markdown",
            key=f"{key_prefix}_download_{artifact.id}",
            width="stretch",
        )
    except Exception as exc:
        st.error(f"Не удалось создать артефакт: {exc}")


def render_generic_artifact_generator(project_id: str):
    artifact_type = st.selectbox(
        t("artifact_type"),
        list(ARTIFACT_PRESETS),
        format_func=lambda value: t(PRESET_TRANSLATION_KEYS[value][0], ARTIFACT_PRESETS[value][0]),
        key="ui_v2_generic_artifact_type",
    )
    title_key, instruction_key = PRESET_TRANSLATION_KEYS[artifact_type]
    default_title, default_instruction = ARTIFACT_PRESETS[artifact_type]
    title = t(title_key, default_title)
    instruction = t(instruction_key, default_instruction)
    render_user_artifact_generator(
        project_id=project_id,
        artifact_type=artifact_type,
        default_title=title,
        default_instruction=instruction,
        key_prefix=f"ui_v2_generic_{artifact_type}",
    )
