import streamlit as st

from repositories.memory_repository import MemoryRepository
from ui.confluence_article import render_confluence_article_tab
from ui.jira_ticket_drafts import render_jira_ticket_drafts_tab
from ui.report import render_report_tab


def render_artifacts_area(memory_repository: MemoryRepository):
    st.markdown("## 📤 Outputs / Artifacts")
    st.caption(
        "Generate delivery-ready outputs from Project Memory and the emerging Project Model."
    )

    tab_report, tab_jira_drafts, tab_confluence_article = st.tabs(
        [
            "📊 Project Report",
            "🧾 Jira Drafts",
            "📝 Confluence Article",
        ]
    )

    with tab_report:
        render_report_tab(memory_repository)

    with tab_jira_drafts:
        render_jira_ticket_drafts_tab(memory_repository)

    with tab_confluence_article:
        render_confluence_article_tab(memory_repository)

