import streamlit as st

from ai.graph_answering import answer_project_question_over_graph
from graph.graph_retriever_v2 import GraphRetrieverV2
from ui_v2.components.user_artifact_generator import (
    render_generic_artifact_generator,
    render_user_artifact_generator,
)
from ui_v2.state import get_chat_artifact, get_current_project_id, set_chat_artifact
from ui_v2.i18n import t


def _set_prompt(prompt: str):
    st.session_state.ui_v2_assistant_question = prompt


def _render_artifact_area(memory_repository):
    selected = get_chat_artifact()

    st.caption(t("artifact_context_caption"))

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
        st.info(t("choose_artifact"))
        return

    if selected == "confluence":
        render_user_artifact_generator(
            project_id=get_current_project_id(),
            artifact_type="confluence_article",
            default_title=t("confluence_artifact_title"),
            default_instruction=t("confluence_artifact_instruction"),
            key_prefix="ui_v2_confluence_artifact",
        )

    elif selected == "all":
        render_generic_artifact_generator(get_current_project_id())

    elif selected == "jira":
        render_user_artifact_generator(
            project_id=get_current_project_id(),
            artifact_type="jira_ticket_drafts",
            default_title=t("jira_artifact_title"),
            default_instruction=t("jira_artifact_instruction"),
            key_prefix="ui_v2_jira_artifact",
        )

    elif selected == "tests":
        render_user_artifact_generator(
            project_id=get_current_project_id(),
            artifact_type="test_cases",
            default_title=t("tests_artifact_title"),
            default_instruction=t("tests_artifact_instruction"),
            key_prefix="ui_v2_tests_artifact",
        )


def render_chat_panel(memory_repository=None):
    tab_chat, tab_artifacts = st.tabs([t("chat"), t("artifacts")])

    with tab_chat:
        st.markdown(
            f"""
            <div class="pb-chat-bubble">
                {t('chat_intro')}
            </div>
            """,
            unsafe_allow_html=True,
        )

        prompts = [(t(f"prompt_{index}"), t(f"prompt_{index}")) for index in range(1, 5)]

        for label, prompt in prompts:
            if st.button(label, key=f"ui_v2_prompt_{label}", width="stretch"):
                _set_prompt(prompt)
                st.rerun()

        question = st.text_area(
            t("question"),
            placeholder=t("ask_question"),
            height=110,
            label_visibility="collapsed",
            key="ui_v2_assistant_question",
        )

        if st.button(t("send"), key="ui_v2_send", width="stretch", type="primary") and question.strip():
            with st.spinner("Project Brain is reading Knowledge Graph..."):
                answer = answer_project_question_over_graph(
                    question,
                    graph_retriever=GraphRetrieverV2(project_id=get_current_project_id()),
                )
            st.markdown(answer)

    with tab_artifacts:
        if memory_repository is None:
            st.info(t("artifact_context_required"))
        else:
            _render_artifact_area(memory_repository)
