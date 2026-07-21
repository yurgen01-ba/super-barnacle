from __future__ import annotations

import streamlit as st
from ui_v2.i18n import t

from ui.confluence import render_confluence_tab
from ui.jira import render_jira_tab
from ui.meetings import render_meetings_tab
from ui.slack import render_slack_tab
from ui.files import render_files_tab


def source_options() -> dict[str, str]:
    return {
        "meetings": t("meetings"),
        "slack": "Slack",
        "confluence": "Confluence",
        "jira": "Jira",
        "files": t("files"),
    }


SOURCE_OPTIONS = source_options()


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
        render_files_tab(memory_repository)
    else:
        st.warning(t("unknown_source", source=source_key))
