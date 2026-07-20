import streamlit as st

from ai.graph_answering import answer_project_question_over_graph
from ui_v2.components.user_artifact_generator import (
    render_generic_artifact_generator,
    render_user_artifact_generator,
)
from ui_v2.state import get_chat_artifact, get_current_project_id, set_chat_artifact


def _set_prompt(prompt: str):
    st.session_state.ui_v2_assistant_question = prompt


def _render_artifact_area(memory_repository):
    selected = get_chat_artifact()

    st.caption("Артефакты будут генерироваться из graph-first контекста проекта.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("▤ Confluence", key="ui_v2_artifact_confluence_btn", width="stretch"):
            set_chat_artifact("confluence")
            st.rerun()

        if st.button("▱ Jira", key="ui_v2_artifact_jira_btn", width="stretch"):
            set_chat_artifact("jira")
            st.rerun()

    with col2:
        if st.button("⌁ Test cases", key="ui_v2_artifact_tests_btn", width="stretch"):
            set_chat_artifact("tests")
            st.rerun()

        if st.button("▣ All artifacts", key="ui_v2_artifact_all_btn", width="stretch"):
            set_chat_artifact("all")
            st.rerun()

    if not selected:
        st.info("Выберите тип артефакта.")
        return

    if selected == "confluence":
        render_user_artifact_generator(
            project_id=get_current_project_id(),
            artifact_type="confluence_article",
            default_title="Статья Confluence",
            default_instruction=(
                "Подготовь готовую к публикации статью Confluence: обзор, цели, процессы, "
                "требования, решения, риски и открытые вопросы. Используй только подтверждённый контекст проекта."
            ),
            key_prefix="ui_v2_confluence_artifact",
        )

    elif selected == "all":
        render_generic_artifact_generator(get_current_project_id())

    elif selected == "jira":
        render_user_artifact_generator(
            project_id=get_current_project_id(),
            artifact_type="jira_ticket_drafts",
            default_title="Черновики Jira-задач",
            default_instruction=(
                "Создай набор Jira-ready задач. Для каждой укажи тип, summary, description, "
                "priority, acceptance criteria, зависимости и вопросы для аналитика. Не выдумывай требования."
            ),
            key_prefix="ui_v2_jira_artifact",
        )

    elif selected == "tests":
        render_user_artifact_generator(
            project_id=get_current_project_id(),
            artifact_type="test_cases",
            default_title="Тест-кейсы",
            default_instruction=(
                "Создай тест-кейсы по подтверждённым требованиям и бизнес-правилам. Для каждого укажи "
                "предусловия, шаги, ожидаемый результат, приоритет и связь с требованием. Добавь негативные сценарии."
            ),
            key_prefix="ui_v2_tests_artifact",
        )


def render_chat_panel(memory_repository=None):
    tab_chat, tab_artifacts = st.tabs(["Чат", "Артефакты"])

    with tab_chat:
        st.markdown(
            """
            <div class="pb-chat-bubble">
                Задавайте вопросы по проекту. Ответ будет строиться через Project Knowledge Graph.
            </div>
            """,
            unsafe_allow_html=True,
        )

        prompts = [
            ("Опиши проект OrgMeter", "Опиши проект OrgMeter вкратце"),
            ("Какие изменения были сегодня?", "Какие изменения были сегодня?"),
            ("Покажи процесс Funding", "Покажи процесс Funding"),
            ("Найди противоречия в правилах", "Найди противоречия в правилах"),
        ]

        for label, prompt in prompts:
            if st.button(label, key=f"ui_v2_prompt_{label}", width="stretch"):
                _set_prompt(prompt)
                st.rerun()

        question = st.text_area(
            "Question",
            placeholder="Задайте вопрос...",
            height=110,
            label_visibility="collapsed",
            key="ui_v2_assistant_question",
        )

        if st.button("Отправить", key="ui_v2_send", width="stretch", type="primary") and question.strip():
            with st.spinner("Project Brain is reading Knowledge Graph..."):
                answer = answer_project_question_over_graph(question)
            st.markdown(answer)

    with tab_artifacts:
        if memory_repository is None:
            st.info("Artifacts require memory repository context.")
        else:
            _render_artifact_area(memory_repository)
