import streamlit as st

from ai.graph_answering import answer_project_question_over_graph, stream_project_question_over_graph
from graph.graph_retriever_v2 import GraphRetrieverV2
from providers.text.factory import create_text_provider
from repositories.workspace_repository import workspace_repository
from ui_v2.components.user_artifact_generator import (
    render_generic_artifact_generator,
    render_user_artifact_generator,
)
from ui_v2.state import get_chat_artifact, get_current_project_id, set_chat_artifact
from ui_v2.i18n import t
from ui_v2.loaders import inline_seal_loader


def _queue_prompt(prompt: str, pending_key: str, input_key: str):
    st.session_state[pending_key] = prompt
    st.session_state[input_key] = prompt


def _render_artifact_area(memory_repository):
    selected = get_chat_artifact()

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


def _render_chat_content(
    key_prefix: str,
    *,
    input_height: int = 110,
    compact_prompts: bool = False,
    answer_height: int | None = None,
) -> None:
    pending_key = f"{key_prefix}_pending_question"
    input_key = f"{key_prefix}_question"
    answer_rendered = False
    prompts = [(t(f"prompt_{index}"), t(f"prompt_{index}")) for index in range(1, 5)]

    if compact_prompts:
        for index, ((label, prompt), prompt_column) in enumerate(
            zip(prompts, st.columns(4, gap="small")), start=1
        ):
            with prompt_column:
                st.button(
                    label,
                    key=f"{key_prefix}_prompt_{index}",
                    width="stretch",
                    on_click=_queue_prompt,
                    args=(prompt, pending_key, input_key),
                )
    if compact_prompts:
        question_column, send_column = st.columns(
            [0.82, 0.18], gap="small", vertical_alignment="bottom"
        )
    else:
        question_column = st.container()
        send_column = st.container()

    with question_column:
        question = st.text_area(
            t("question"),
            placeholder=t("ask_question"),
            height=input_height,
            label_visibility="collapsed",
            key=input_key,
        )

    if not compact_prompts:
        for index, (label, prompt) in enumerate(prompts, start=1):
            st.button(
                label,
                key=f"{key_prefix}_prompt_{index}",
                width="stretch",
                on_click=_queue_prompt,
                args=(prompt, pending_key, input_key),
            )

    with send_column:
        submitted = st.button(
            t("send"),
            key=f"{key_prefix}_send",
            width="stretch",
            type="primary",
        )

    if submitted and question.strip():
        st.session_state[pending_key] = question.strip()

    pending_question = st.session_state.pop(pending_key, "")

    def render_answer() -> None:
        nonlocal answer_rendered
        if pending_question:
            project_id = get_current_project_id()
            settings = workspace_repository.get_settings(project_id)
            try:
                text_provider = create_text_provider(
                    provider_name=settings.get("transcript_extractor_provider", "ollama"),
                    model=settings.get("transcript_extractor_model", "qwen2.5:7b"),
                    host=settings.get("transcript_extractor_host", "http://localhost:11434"),
                    timeout_seconds=min(
                        max(int(settings.get("transcript_extractor_timeout_seconds", 180)), 60),
                        600,
                    ),
                    num_predict=320,
                )
                with inline_seal_loader(t("chat_reading_graph")):
                    if hasattr(st, "write_stream"):
                        answer = st.write_stream(
                            stream_project_question_over_graph(
                                pending_question,
                                text_provider=text_provider,
                                graph_retriever=GraphRetrieverV2(project_id=project_id),
                            )
                        )
                        answer_rendered = True
                    else:
                        answer = answer_project_question_over_graph(
                            pending_question,
                            text_provider=text_provider,
                            graph_retriever=GraphRetrieverV2(project_id=project_id),
                        )
            except Exception as exc:
                answer = t("chat_model_error").format(error=str(exc))
            st.session_state.ui_v2_last_answer = answer

        if st.session_state.get("ui_v2_last_answer") and not answer_rendered:
            st.markdown(st.session_state.ui_v2_last_answer)

    if answer_height:
        with st.container(
            height=answer_height,
            border=True,
            key=f"{key_prefix}_answer_panel",
        ):
            render_answer()
    else:
        render_answer()


def _open_fullscreen_chat() -> None:
    @st.dialog(t("chat"), width="large")
    def _dialog() -> None:
        st.markdown('<span class="pb-fullscreen-chat-marker"></span>', unsafe_allow_html=True)
        _render_chat_content(
            "ui_v2_fullscreen_chat",
            input_height=82,
            compact_prompts=True,
            answer_height=430,
        )

    _dialog()


@st.fragment
def render_chat_panel(memory_repository=None):
    tab_chat, tab_artifacts = st.tabs([t("chat"), t("artifacts")])

    with tab_chat:
        _, expand_col = st.columns([0.82, 0.18])
        with expand_col:
            if st.button(
                "⛶",
                key="ui_v2_expand_chat",
                help=t("expand_chat"),
                width="stretch",
            ):
                _open_fullscreen_chat()

        _render_chat_content("ui_v2_chat")

    with tab_artifacts:
        if memory_repository is None:
            st.info(t("artifact_context_required"))
        else:
            _render_artifact_area(memory_repository)
