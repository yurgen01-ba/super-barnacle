import streamlit as st

from ai.report_generator import generate_project_report
from progress.progress_manager import ProgressManager
from repositories.memory_repository import MemoryRepository


def render_report_tab(memory_repository: MemoryRepository):
    st.header("Project report")

    memory_items = memory_repository.get_memory_items()
    st.info(f"Project Memory contains {len(memory_items)} knowledge items.")

    report_mode = "executive"
    try:
        report_mode = st.radio(
            "Report mode",
            options=["executive", "analyst"],
            index=0,
            help="Executive is shorter and cheaper. Analyst is more detailed.",
        )
    except Exception:
        # Backward compatibility if report generator does not support modes yet.
        report_mode = "executive"

    if st.button("Generate report"):
        if not memory_items:
            st.warning("Project Memory is empty. Add Slack, Jira, or Meeting data first.")
            return

        progress = ProgressManager("Generating project report", total_steps=3)

        try:
            progress.step("Preparing compact Project Memory")
            progress.step("Generating report with Claude")

            try:
                report = generate_project_report(memory_items, mode=report_mode)
            except TypeError:
                report = generate_project_report(memory_items)

            progress.step("Rendering report")

            st.success("Report generated successfully.")
            st.markdown("## Generated Project Report")
            st.write(report)

            progress.done("Report generation completed.")

        except Exception as exc:
            progress.error("Failed to generate report")
            st.exception(exc)

