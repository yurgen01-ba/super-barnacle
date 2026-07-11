import streamlit as st

from repositories.memory_repository import MemoryRepository
from ui.confluence import render_confluence_tab
from ui.jira import render_jira_tab
from ui.jobs_panel import render_jobs_panel
from ui.meetings import render_meetings_tab
from ui.slack import render_slack_tab


def render_sources_area(memory_repository: MemoryRepository):
    st.markdown("## 📥 Inputs / Sources")
    st.caption(
        "Add raw project materials here. Project Brain will parse them, save source documents/chunks, "
        "extract structured knowledge, and build the Project Model foundation."
    )

    with st.expander("Background extraction jobs", expanded=False):
        render_jobs_panel()

    tab_meetings, tab_slack, tab_jira, tab_confluence = st.tabs(
        [
            "🎥 Meetings",
            "💬 Slack",
            "📋 Jira",
            "📚 Confluence",
        ]
    )

    with tab_meetings:
        render_meetings_tab(memory_repository)

    with tab_slack:
        render_slack_tab(memory_repository)

    with tab_jira:
        render_jira_tab(memory_repository)

    with tab_confluence:
        render_confluence_tab(memory_repository)
