from __future__ import annotations

import streamlit as st

from repositories.slack_connection_repository import slack_connection_repository
from services.slack_oauth_service import slack_oauth_service
from ui_v2.auth import get_authenticated_user
from ui_v2.i18n import t
from ui_v2.state import get_current_project_id


def render_slack_oauth_callback() -> bool:
    params = st.query_params
    if str(params.get("slack_callback", "")) != "1":
        return False
    state = str(params.get("state", "") or "")
    if params.get("error"):
        if state:
            slack_connection_repository.consume_state(state)
        st.error(t("slack_authorization_denied"))
        st.caption(str(params.get("error", "") or ""))
        st.info(t("oauth_close_tab"))
        return True
    try:
        result = slack_oauth_service.complete_authorization(
            str(params.get("code", "") or ""), state
        )
    except Exception as exc:
        st.error(t("slack_connection_failed", error=str(exc)))
    else:
        st.success(t("slack_connected", workspace=result["connection"]["team_name"]))
        st.info(t("oauth_close_tab"))
    return True


def render_slack_oauth_settings() -> None:
    user = get_authenticated_user() or {}
    user_id = str(user.get("id") or "")
    project_id = get_current_project_id()
    st.markdown(f"#### {t('slack_oauth_title')}")
    st.caption(t("slack_oauth_caption"))

    if not slack_oauth_service.configured:
        st.warning(t("slack_oauth_unavailable"))
        return

    connect_url = slack_oauth_service.authorization_url(user_id, project_id)
    st.link_button(
        t("connect_slack_oauth"), connect_url, type="primary", icon=":material/link:",
    )
    connections = slack_connection_repository.list_for_project(project_id, user_id)
    for connection in connections:
        with st.container(border=True):
            name_col, action_col = st.columns([0.7, 0.3])
            with name_col:
                st.markdown(f"**{connection['team_name']}**")
                st.caption(t("oauth_connected"))
            with action_col:
                if st.button(
                    t("disconnect_slack"), key=f"disconnect_slack_{connection['id']}",
                    width="stretch",
                ):
                    slack_oauth_service.disconnect(connection["id"], user_id, project_id)
                    st.success(t("slack_disconnected"))
                    st.rerun()
