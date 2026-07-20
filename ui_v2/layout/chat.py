import streamlit as st

from ai.graph_answering import answer_project_question_over_graph
from ui_v2.state import get_chat_artifact, set_chat_artifact


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
        try:
            from ui.confluence_article import render_confluence_article_tab

            render_confluence_article_tab(memory_repository)
        except Exception as exc:
            st.warning("Confluence article generator is not available in this build.")
            st.caption(str(exc))

    elif selected == "all":
        try:
            from ui.workspace.artifacts import render_artifacts_area

            render_artifacts_area(memory_repository)
        except Exception as exc:
            st.warning("Artifacts workspace is not available in this build.")
            st.caption(str(exc))

    elif selected == "jira":
        st.info("Jira artifact generator entry-point is defined, but the UI generator is not connected yet.")
        st.button("Generate Jira from graph context", key="ui_v2_jira_placeholder", disabled=True)

    elif selected == "tests":
        st.info("Test case generator entry-point is defined, but the UI generator is not connected yet.")
        st.button("Generate test cases from graph context", key="ui_v2_tests_placeholder", disabled=True)


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
