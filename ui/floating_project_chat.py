import streamlit as st

from ai.project_chat import answer_project_question
from providers.text.health import check_ollama_text_model
from repositories.chat_context_repository import ChatContextRepository
from repositories.memory_repository import MemoryRepository


def _inject_floating_chat_css():
    st.markdown(
        """
        <style>
            section[data-testid="stSidebar"] {
                z-index: 100;
            }

            .project-chat-note {
                font-size: 0.85rem;
                color: #666;
                margin-bottom: 0.5rem;
            }

            div[data-testid="stPopover"] {
                z-index: 999999;
            }

            div[data-testid="stPopover"] > div {
                max-width: 620px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _ensure_chat_state():
    if "floating_project_chat_messages" not in st.session_state:
        st.session_state.floating_project_chat_messages = []

    if "floating_project_chat_last_context" not in st.session_state:
        st.session_state.floating_project_chat_last_context = None


def render_floating_project_chat(memory_repository: MemoryRepository):
    _inject_floating_chat_css()
    _ensure_chat_state()

    context_repository = ChatContextRepository()

    with st.container():
        _, right = st.columns([0.78, 0.22])

        with right:
            with st.popover("💬 Project Chat 2.0", width="stretch"):
                st.markdown("### Project Chat 2.0")
                st.markdown(
                    '<div class="project-chat-note">Intent-aware chat using Project Summary, Entities, Relationships, Facts, Memory, and Chunks.</div>',
                    unsafe_allow_html=True,
                )

                memory_items = memory_repository.get_memory_items()
                st.caption(f"Memory items: {len(memory_items)}")

                with st.expander("Settings", expanded=False):
                    col1, col2 = st.columns(2)

                    with col1:
                        chat_model = st.selectbox(
                            "Model",
                            options=["qwen2.5:7b", "qwen2.5:3b", "qwen2.5:14b"],
                            index=0,
                            key="floating_project_chat_model",
                        )

                    with col2:
                        answer_language = st.selectbox(
                            "Language",
                            options=["same_as_question", "english", "russian"],
                            index=0,
                            format_func=lambda value: {
                                "same_as_question": "Same",
                                "english": "English",
                                "russian": "Russian",
                            }[value],
                            key="floating_project_chat_answer_language",
                        )

                    chat_host = st.text_input(
                        "Ollama host",
                        value="http://localhost:11434",
                        key="floating_project_chat_host",
                    )

                    chat_timeout = st.slider(
                        "Timeout, seconds",
                        60,
                        600,
                        240,
                        30,
                        key="floating_project_chat_timeout",
                    )

                    col3, col4 = st.columns(2)

                    with col3:
                        knowledge_limit = st.slider(
                            "Memory limit",
                            5,
                            80,
                            35,
                            5,
                            key="floating_project_chat_knowledge_limit",
                        )

                    with col4:
                        chunk_limit = st.slider(
                            "Chunks limit",
                            0,
                            30,
                            12,
                            1,
                            key="floating_project_chat_chunk_limit",
                        )

                    if st.button("Test model", key="floating_project_chat_test_model"):
                        health = check_ollama_text_model(
                            host=chat_host,
                            model=chat_model,
                        )

                        if health["ok"] and health["model_available"]:
                            st.success(f"Model available: {chat_model}")
                        elif health["ok"]:
                            st.warning(f"Ollama works, but model not found: {chat_model}")
                        else:
                            st.error("Ollama is not reachable.")

                        st.write(health)

                chat_box = st.container(height=390)

                with chat_box:
                    for message in st.session_state.floating_project_chat_messages:
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])

                question = st.text_area(
                    "Question",
                    height=90,
                    placeholder="Ask about project overview, Merchant, risks, requirements, dependencies...",
                    key="floating_project_chat_question",
                    label_visibility="collapsed",
                )

                col_send, col_clear = st.columns([0.7, 0.3])

                with col_send:
                    send_clicked = st.button(
                        "Ask",
                        width="stretch",
                        key="floating_project_chat_ask",
                    )

                with col_clear:
                    clear_clicked = st.button(
                        "Clear",
                        width="stretch",
                        key="floating_project_chat_clear",
                    )

                if clear_clicked:
                    st.session_state.floating_project_chat_messages = []
                    st.session_state.floating_project_chat_last_context = None
                    st.rerun()

                if send_clicked and question.strip():
                    st.session_state.floating_project_chat_messages.append(
                        {"role": "user", "content": question.strip()}
                    )

                    with st.spinner("Classifying intent, retrieving Project Model context, and generating answer..."):
                        context = context_repository.search_context(
                            question,
                            knowledge_limit=knowledge_limit,
                            chunk_limit=chunk_limit,
                        )

                        answer = answer_project_question(
                            question=question,
                            context=context,
                            model=chat_model,
                            host=chat_host,
                            timeout_seconds=chat_timeout,
                            answer_language=answer_language,
                        )

                    st.session_state.floating_project_chat_messages.append(
                        {"role": "assistant", "content": answer}
                    )
                    st.session_state.floating_project_chat_last_context = context
                    st.rerun()

                if st.session_state.floating_project_chat_last_context:
                    with st.expander("Context used", expanded=False):
                        st.write(st.session_state.floating_project_chat_last_context)

