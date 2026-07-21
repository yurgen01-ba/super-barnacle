from __future__ import annotations

import streamlit as st

from jobs.extraction_tasks import process_local_browser_sync_job
from jobs.knowledge_extraction_service import KnowledgeExtractionJobService
from services.local_browser_connector import (
    LocalBrowserConnectorError,
    local_browser_session_registry,
)
from ui_v2.auth import get_authenticated_email, get_authenticated_user
from ui_v2.i18n import t
from ui_v2.state import get_current_project_id


DEFAULT_URLS = {
    "atlassian": "https://your-company.atlassian.net",
    "slack": "https://app.slack.com/client",
}


def render_local_browser_connector(
    provider: str, *, atlassian_products: tuple[str, ...] | None = None
) -> None:
    user = get_authenticated_user() or {}
    user_id = str(user.get("id") or "")
    project_id = get_current_project_id()
    if not user_id:
        return

    st.markdown(f"#### {t('local_browser_connector')}")
    st.caption(t("local_browser_connector_caption"))
    session = local_browser_session_registry.find(
        user_id=user_id, project_id=project_id, provider=provider
    )

    if not session:
        site_url = st.text_input(
            t("browser_site_url"),
            placeholder=DEFAULT_URLS[provider],
            key=f"local_browser_url_{provider}_{project_id}",
            help=t(f"browser_site_url_help_{provider}"),
        )
        if st.button(
            t("open_secure_browser"), key=f"open_local_browser_{provider}",
            icon=":material/open_in_new:",
        ):
            try:
                local_browser_session_registry.start(
                    user_id=user_id, project_id=project_id,
                    provider=provider, start_url=site_url,
                )
            except (ValueError, LocalBrowserConnectorError) as exc:
                st.error(str(exc))
            else:
                st.success(t("browser_opened_login"))
                st.rerun()
        return

    pages = session.get("pages") or []
    st.success(t("browser_session_active"))
    if pages:
        current = pages[0]
        st.caption(f"{current.get('title') or provider}: {current.get('url')}")
    st.info(t("browser_login_instruction"))

    selected_products = set(atlassian_products or ("jira", "confluence"))
    sync_jira = "jira" in selected_products
    sync_confluence = "confluence" in selected_products
    if provider == "atlassian":
        if atlassian_products is None:
            jira_col, confluence_col = st.columns(2)
            with jira_col:
                sync_jira = st.checkbox(
                    "Jira", value=True, key=f"browser_sync_jira_{session['id']}"
                )
            with confluence_col:
                sync_confluence = st.checkbox(
                    "Confluence", value=True, key=f"browser_sync_confluence_{session['id']}"
                )
        else:
            st.caption(t("browser_import_product", product=" + ".join(
                name.title() for name in atlassian_products
            )))

    sync_col, refresh_col, close_col = st.columns([0.5, 0.25, 0.25])
    with sync_col:
        if st.button(
            t("import_from_open_browser"),
            key=f"browser_sync_{provider}_{session['id']}",
            type="primary", disabled=bool(session.get("busy")),
        ):
            service = KnowledgeExtractionJobService()
            job = service.start(
                process_local_browser_sync_job,
                session_id=session["id"], user_id=user_id, provider=provider,
                project_id=project_id, sync_jira=sync_jira,
                sync_confluence=sync_confluence,
                metadata={
                    "source": f"local_browser_{provider}",
                    "project_id": project_id,
                    "notification_email": get_authenticated_email(),
                },
            )
            st.session_state["latest_knowledge_extraction_job_id"] = job.id
            st.success(t("browser_sync_started"))
            st.rerun()
    with refresh_col:
        if st.button(
            t("check_login"), key=f"browser_refresh_{provider}_{session['id']}",
            icon=":material/refresh:", width="stretch",
        ):
            st.rerun()
    with close_col:
        if st.button(
            t("close_browser"), key=f"browser_close_{provider}_{session['id']}",
            icon=":material/close:", width="stretch",
        ):
            local_browser_session_registry.close(
                session["id"], user_id=user_id, project_id=project_id
            )
            st.success(t("browser_session_deleted"))
            st.rerun()
