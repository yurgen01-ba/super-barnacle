import streamlit as st

from ai.project_chat import answer_project_question
from providers.text.health import check_ollama_text_model
from repositories.chat_context_repository import ChatContextRepository
from repositories.memory_repository import MemoryRepository


def render_project_chat_tab(memory_repository: MemoryRepository):
    st.header("Project Chat")
    st.caption("Ask questions about the project using Project Memory, source documents, and chunks.")

    context_repository = ChatContextRepository()
    memory_items = memory_repository.get_memory_items()

    st.info(f"Project Memory contains {len(memory_items)} knowledge items.")

    if "project_chat_messages" not in st.session_state:
        st.session_state.project_chat_messages = []

    with st.expander("Chat settings", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            chat_model = st.selectbox(
                "Local chat model",
                options=["qwen2.5:7b", "qwen2.5:3b", "qwen2.5:14b"],
                index=0,
                key="project_chat_model",
            )

        with col2:
            answer_language = st.selectbox(
                "Answer language",
                options=["same_as_question", "english", "russian"],
                index=0,
                format_func=lambda value: {
                    "same_as_question": "Same as question",
                    "english": "English",
                    "russian": "Russian",
                }[value],
                key="project_chat_answer_language",
            )

        col3, col4 = st.columns(2)

        with col3:
            chat_host = st.text_input(
                "Ollama host",
                value="http://localhost:11434",
                key="project_chat_host",
            )

        with col4:
            chat_timeout = st.slider(
                "Timeout, seconds",
                60,
                420,
                180,
                30,
                key="project_chat_timeout",
            )

        col5, col6 = st.columns(2)

        with col5:
            knowledge_limit = st.slider(
                "Memory items limit",
                5,
                50,
                20,
                5,
                key="project_chat_knowledge_limit",
            )

        with col6:
            chunk_limit = st.slider(
                "Source chunks limit",
                0,
                20,
                8,
                1,
                key="project_chat_chunk_limit",
            )

        if st.button("Test chat model", key="test_project_chat_model"):
            health = check_ollama_text_model(host=chat_host, model=chat_model)

            if health["ok"] and health["model_available"]:
                st.success(f"Ollama is running. Chat model available: {chat_model}")
                st.write(health)
            elif health["ok"]:
                st.warning(f"Ollama is running, but model not found: {chat_model}")
                st.write(health)
            else:
                st.error("Ollama is not reachable.")
                st.write(health)

    for message in st.session_state.project_chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask a question about the project...")

    if question:
        st.session_state.project_chat_messages.append({"role": "user", "content": question})

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching Project Memory and generating answer..."):
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

                st.markdown(answer)

                with st.expander("Context used", expanded=False):
                    st.write(context)

        st.session_state.project_chat_messages.append({"role": "assistant", "content": answer})

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("Clear chat", key="clear_project_chat"):
            st.session_state.project_chat_messages = []
            st.rerun()

    with col_b:
        if st.button("Show latest context sample", key="show_project_chat_context_sample"):
            context = context_repository.search_context(
                "",
                knowledge_limit=knowledge_limit,
                chunk_limit=chunk_limit,
            )
            st.write(context)

