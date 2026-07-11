import streamlit as st

from config import DB_PATH
from repositories.memory_repository import MemoryRepository
from repositories.source_repository import SourceRepository


def render_memory_tab(memory_repository: MemoryRepository):
    source_repository = SourceRepository()

    st.header("Project Memory")
    st.caption(f"DB path: {DB_PATH}")

    memory_items = memory_repository.get_memory_items()
    timeline_items = memory_repository.get_timeline_items()
    documents = source_repository.list_documents()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Knowledge items", len(memory_items))

    with col2:
        st.metric("Timeline events", len(timeline_items))

    with col3:
        st.metric("Source documents", len(documents))

    tab_knowledge, tab_sources, tab_timeline = st.tabs([
        "Knowledge",
        "Sources & Chunks",
        "Timeline",
    ])

    with tab_knowledge:
        st.subheader(f"Knowledge items: {len(memory_items)}")
        st.write(memory_items)

    with tab_sources:
        st.subheader(f"Source documents: {len(documents)}")
        st.write(documents)

        if documents:
            document_options = {
                f"#{doc['id']} | {doc['source_type']} | {doc['name']}": doc["id"]
                for doc in documents
            }

            selected_document = st.selectbox(
                "Preview chunks for document",
                options=list(document_options.keys()),
            )

            document_id = document_options[selected_document]
            chunks = source_repository.list_chunks(document_id=document_id, limit=50)

            st.subheader(f"Chunks for document #{document_id}: {len(chunks)}")

            for chunk in chunks:
                with st.expander(
                    f"Chunk {chunk['chunk_index']} | length={chunk['content_length']}",
                    expanded=False,
                ):
                    st.text_area(
                        "Content",
                        chunk["content"][:8000],
                        height=250,
                        key=f"chunk_{chunk['id']}",
                    )

    with tab_timeline:
        st.subheader(f"Timeline events: {len(timeline_items)}")
        st.write(timeline_items)

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("Clear Project Memory"):
            memory_repository.clear()
            st.success("Project Memory and Timeline cleared. Refresh the page.")

    with col_b:
        if st.button("Clear Source Documents"):
            source_repository.clear()
            st.success("Source documents and chunks cleared. Refresh the page.")

