import streamlit as st

from builders.project_summary_builder import ProjectSummaryBuilder
from providers.text.health import check_ollama_text_model
from repositories.project_repository import ProjectRepository


def render_project_summary_tab():
    st.header("Project Summary")
    st.caption(
        "A stable high-level project model generated from Canonical Facts, Entities, and Relationships."
    )

    project_repository = ProjectRepository()

    with st.expander("Builder settings", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            model = st.selectbox(
                "Summary model",
                options=["qwen2.5:7b", "qwen2.5:3b", "qwen2.5:14b"],
                index=0,
                key="project_summary_model",
            )

        with col2:
            timeout_seconds = st.slider(
                "Timeout, seconds",
                120,
                600,
                300,
                30,
                key="project_summary_timeout",
            )

        host = st.text_input(
            "Ollama host",
            value="http://localhost:11434",
            key="project_summary_host",
        )

        if st.button("Test summary model", key="test_project_summary_model"):
            health = check_ollama_text_model(host=host, model=model)

            if health["ok"] and health["model_available"]:
                st.success(f"Ollama is running. Model available: {model}")
            elif health["ok"]:
                st.warning(f"Ollama is running, but model not found: {model}")
            else:
                st.error("Ollama is not reachable.")

            st.write(health)

    stats = project_repository.get_model_statistics()

    with st.expander("Current model statistics", expanded=True):
        st.write(stats)

    if st.button("Build / Refresh Project Summary", key="build_project_summary"):
        with st.spinner("Building Project Summary from facts, entities, and relationships..."):
            result = ProjectSummaryBuilder(
                model=model,
                host=host,
                timeout_seconds=timeout_seconds,
            ).build_and_save_summary()

        st.success(f"Project Summary saved. ID: {result['summary_id']}")

        with st.expander("Generation context", expanded=False):
            st.write(result["context"])

    latest = project_repository.get_latest_summary()

    st.subheader("Latest Project Summary")

    if not latest:
        st.info("No Project Summary yet. Build it after extracting facts/entities/relationships.")
    else:
        st.caption(f"Version: {latest['version']} | Updated: {latest['updated_at']}")
        st.markdown(latest.get("summary") or "")

    with st.expander("Previous summaries", expanded=False):
        summaries = project_repository.list_summaries(limit=20)

        if not summaries:
            st.caption("No previous summaries.")
        else:
            for summary in summaries:
                with st.expander(
                    f"#{summary['id']} | v{summary['version']} | {summary['updated_at']}",
                    expanded=False,
                ):
                    st.markdown(summary.get("summary") or "")
                    st.write(
                        {
                            "id": summary["id"],
                            "title": summary["title"],
                            "version": summary["version"],
                            "metadata_json": summary.get("metadata_json"),
                            "created_at": summary["created_at"],
                            "updated_at": summary["updated_at"],
                        }
                    )

