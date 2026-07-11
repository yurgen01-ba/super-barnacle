from __future__ import annotations

import streamlit as st

from ui.confluence import render_confluence_tab
from ui.jira import render_jira_tab
from ui.meetings import render_meetings_tab
from ui.slack import render_slack_tab


SOURCE_OPTIONS = {
    "meetings": "🎥 Meetings",
    "slack": "💬 Slack",
    "confluence": "📚 Confluence",
    "jira": "🎫 Jira",
    "files": "📁 Files",
}


def render_source_adapter(source_key: str, memory_repository):
    if source_key == "meetings":
        render_meetings_tab(memory_repository)
    elif source_key == "slack":
        render_slack_tab(memory_repository)
    elif source_key == "confluence":
        render_confluence_tab(memory_repository)
    elif source_key == "jira":
        render_jira_tab(memory_repository)
    elif source_key == "files":
        st.info("Files importer is not connected yet.")
        st.button("Upload files", key="ui_v2_files_upload_placeholder", disabled=True)
    else:
        st.warning(f"Unknown source: {source_key}")
