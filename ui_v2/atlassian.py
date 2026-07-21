from __future__ import annotations

import streamlit as st

from jobs.extraction_tasks import process_atlassian_sync_job
from jobs.knowledge_extraction_service import KnowledgeExtractionJobService
from repositories.atlassian_connection_repository import atlassian_connection_repository
from services.atlassian_oauth_service import atlassian_oauth_service
from ui_v2.auth import get_authenticated_email, get_authenticated_user
from ui_v2.i18n import t
from ui_v2.state import get_current_project_id
from ui_v2.browser_connectors import render_local_browser_connector


def render_atlassian_oauth_callback() -> bool:
    """Handle the provider callback before the Project Brain auth gate."""
    params = st.query_params
    # Do not capture callback parameters that belong to Project Brain/Auth0.
    if str(params.get("atlassian_callback", "")) != "1":
        return False
    state = str(params.get("state", "") or "")
    if params.get("error"):
        if state:
            atlassian_connection_repository.consume_state(state)
        st.error(t("atlassian_authorization_denied"))
        st.caption(str(params.get("error_description", "") or ""))
        st.info(t("atlassian_close_tab"))
        return True
    try:
        result = atlassian_oauth_service.complete_authorization(
            str(params.get("code", "") or ""), state
        )
    except Exception as exc:
        st.error(t("atlassian_connection_failed", error=str(exc)))
    else:
        names = ", ".join(site.get("name", "Atlassian") for site in result["sites"])
        st.success(t("atlassian_connected_sites", sites=names))
        st.info(t("atlassian_close_tab"))
    return True


def render_atlassian_settings() -> None:
    user = get_authenticated_user() or {}
    project_id = get_current_project_id()
    st.divider()
    st.subheader(t("atlassian_integration"))
    st.caption(t("atlassian_integration_caption"))

    if not atlassian_oauth_service.configured:
        st.warning(t("atlassian_not_configured"))
        st.code(
            "ATLASSIAN_CLIENT_ID=...\n"
            "ATLASSIAN_CLIENT_SECRET=...\n"
            "ATLASSIAN_REDIRECT_URI=http://localhost:8501/?atlassian_callback=1",
            language="bash",
        )
        return

    connect_url = atlassian_oauth_service.authorization_url(user["id"], project_id)
    st.link_button(
        t("connect_atlassian"), connect_url, type="primary", icon=":material/link:",
        help=t("connect_atlassian_help"),
    )
    st.caption(t("atlassian_refresh_after_auth"))

    connections = atlassian_connection_repository.list_for_project(project_id, user["id"])
    if not connections:
        st.info(t("atlassian_no_connections"))
    for connection in connections:
        scopes = set(connection.get("scopes", []))
        jira_available = any("jira" in scope for scope in scopes)
        confluence_available = any("confluence" in scope for scope in scopes)
        status_label = t("atlassian_status_" + connection.get("status", "connected"))
        with st.container(border=True):
            st.markdown(f"#### {connection['site_name']}")
            st.caption(f"{connection['site_url']} · {status_label}")
            if connection.get("last_sync_at"):
                st.caption(t("atlassian_last_sync", date=connection["last_sync_at"]))
            jira_col, confluence_col = st.columns(2)
            with jira_col:
                sync_jira = st.checkbox(
                    "Jira", value=jira_available, disabled=not jira_available,
                    key=f"atlassian_jira_{connection['id']}",
                )
            with confluence_col:
                sync_confluence = st.checkbox(
                    "Confluence", value=confluence_available, disabled=not confluence_available,
                    key=f"atlassian_confluence_{connection['id']}",
                )
            sync_col, remove_col = st.columns([0.72, 0.28])
            with sync_col:
                if st.button(
                    t("sync_all_accessible"), key=f"sync_atlassian_{connection['id']}",
                    type="primary", disabled=not (sync_jira or sync_confluence),
                ):
                    service = KnowledgeExtractionJobService()
                    job = service.start(
                        process_atlassian_sync_job,
                        connection_id=connection["id"], user_id=user["id"],
                        project_id=project_id, sync_jira=sync_jira,
                        sync_confluence=sync_confluence,
                        metadata={
                            "source": "atlassian_oauth", "project_id": project_id,
                            "site": connection["site_name"],
                            "notification_email": get_authenticated_email(),
                        },
                    )
                    st.session_state["latest_knowledge_extraction_job_id"] = job.id
                    st.success(t("atlassian_sync_started"))
                    st.rerun()
            with remove_col:
                if st.button(
                    t("disconnect"), key=f"disconnect_atlassian_{connection['id']}",
                    icon=":material/link_off:",
                ):
                    atlassian_connection_repository.delete(
                        connection["id"], user["id"], project_id
                    )
                    st.success(t("atlassian_disconnected"))
                    st.rerun()

    st.divider()
    render_local_browser_connector("atlassian")
