from __future__ import annotations

import streamlit as st

from repositories.atlassian_connection_repository import atlassian_connection_repository
from repositories.slack_connection_repository import slack_connection_repository
from services.slack_oauth_service import slack_oauth_service
from ui_v2.auth import get_authenticated_user
from ui_v2.browser_connectors import (
    render_atlassian_oauth_source_connector,
    render_local_browser_connector,
)
from ui_v2.i18n import t
from ui_v2.slack_oauth import render_slack_oauth_settings
from ui_v2.state import (
    get_connection_settings,
    get_current_project_id,
    open_connection_settings,
    set_connection_settings,
)


PROVIDERS = ("jira", "confluence", "slack")


def _atlassian_connections(product: str) -> list[dict]:
    user = get_authenticated_user() or {}
    connections = atlassian_connection_repository.list_for_project(
        get_current_project_id(), str(user.get("id") or "")
    )
    return [
        connection for connection in connections
        if any(product in scope for scope in connection.get("scopes", []))
    ]


def source_oauth_connected(provider: str) -> bool:
    user = get_authenticated_user() or {}
    user_id = str(user.get("id") or "")
    project_id = get_current_project_id()
    if provider in {"jira", "confluence"}:
        return bool(_atlassian_connections(provider))
    if provider == "slack":
        return bool(slack_connection_repository.list_for_project(project_id, user_id))
    return False


def _disconnect(provider: str) -> None:
    user = get_authenticated_user() or {}
    user_id = str(user.get("id") or "")
    project_id = get_current_project_id()
    if provider in {"jira", "confluence"}:
        for connection in _atlassian_connections(provider):
            atlassian_connection_repository.delete(connection["id"], user_id, project_id)
    elif provider == "slack":
        for connection in slack_connection_repository.list_for_project(project_id, user_id):
            slack_oauth_service.disconnect(connection["id"], user_id, project_id)


def render_source_authorization(provider: str) -> None:
    connected = source_oauth_connected(provider)
    label = t(
        "disconnect_source" if connected else "authorize_source",
        source=t(f"source_name_{provider}"),
    )
    if st.button(
        label,
        key=f"source_authorization_{provider}",
        type="secondary" if connected else "primary",
        icon=":material/link_off:" if connected else ":material/login:",
    ):
        if connected:
            _disconnect(provider)
            st.success(t("source_disconnected", source=t(f"source_name_{provider}")))
        else:
            open_connection_settings(provider)
        st.rerun()


def render_connection_settings_hub() -> None:
    st.subheader(t("source_connections"))
    st.caption(t("source_connections_caption"))
    current = get_connection_settings()
    selected = st.radio(
        t("choose_connection_source"),
        PROVIDERS,
        index=PROVIDERS.index(current),
        format_func=lambda provider: t(f"source_name_{provider}"),
        horizontal=True,
        key="connection_settings_selector",
        label_visibility="collapsed",
    )
    set_connection_settings(selected)

    with st.container(border=True, key=f"connection_settings_{selected}"):
        if selected in {"jira", "confluence"}:
            render_atlassian_oauth_source_connector(selected)
            st.markdown('<div class="pb-compact-divider"></div>', unsafe_allow_html=True)
            render_local_browser_connector(
                "atlassian", atlassian_products=(selected,)
            )
        else:
            render_slack_oauth_settings()
            st.markdown('<div class="pb-compact-divider"></div>', unsafe_allow_html=True)
            render_local_browser_connector("slack")
