import streamlit as st

from ai.jira_ticket_generator import generate_jira_ticket_drafts_markdown
from progress.progress_manager import ProgressManager
from repositories.memory_repository import MemoryRepository


def render_jira_ticket_drafts_tab(memory_repository: MemoryRepository):
    st.header("Jira Ticket Drafts")
    st.caption(
        "Generate Jira-ready issue drafts from Project Memory. "
        "AI decides how many tickets are logically needed."
    )

    memory_items = memory_repository.get_memory_items()
    st.info(f"Project Memory contains {len(memory_items)} knowledge items.")

    if not memory_items:
        st.warning("Add and process at least one source before generating Jira tickets.")
        return

    col1, col2 = st.columns(2)

    with col1:
        ticket_style = st.selectbox(
            "Ticket style",
            options=[
                "mixed",
                "user_story",
                "technical_task",
                "bug",
            ],
            index=0,
            format_func=lambda value: {
                "mixed": "AI decides issue types",
                "user_story": "Prefer User Stories",
                "technical_task": "Prefer Technical Tasks",
                "bug": "Prefer Bugs",
            }[value],
        )

    with col2:
        granularity = st.selectbox(
            "Ticket granularity",
            options=[
                "balanced",
                "coarse",
                "fine",
            ],
            index=0,
            format_func=lambda value: {
                "balanced": "Balanced",
                "coarse": "Coarse: fewer larger tickets",
                "fine": "Fine: smaller implementation tickets",
            }[value],
        )

    project_context = st.text_area(
        "Optional project context",
        height=120,
        placeholder=(
            "Example: This is a fintech onboarding project. Prefer backend-ready tasks. "
            "Use concise Jira style."
        ),
    )

    if st.button("Generate Jira ticket drafts"):
        progress = ProgressManager("Generating Jira ticket drafts", total_steps=3)

        try:
            progress.step("Preparing Project Memory for logical ticket splitting")
            progress.step("Generating Jira tickets with Claude")

            markdown = generate_jira_ticket_drafts_markdown(
                memory_items=memory_items,
                project_context=project_context,
                ticket_style=ticket_style,
                granularity=granularity,
            )

            progress.step("Rendering Jira ticket drafts")

            if not markdown:
                st.warning("No Jira ticket drafts were generated. Project Memory may be too generic or empty.")
                progress.done("No tickets generated")
                return

            st.success("Jira ticket drafts generated.")
            st.markdown(markdown)

            st.download_button(
                "Download Jira tickets as Markdown",
                data=markdown,
                file_name="jira_ticket_drafts.md",
                mime="text/markdown",
            )

            progress.done("Jira ticket generation completed.")

        except Exception as exc:
            progress.error("Failed to generate Jira ticket drafts")
            st.exception(exc)

