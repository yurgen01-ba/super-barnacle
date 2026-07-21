from __future__ import annotations

from html import escape
import os

import streamlit as st

from repositories.workspace_repository import workspace_repository
from repositories.user_repository import user_repository
from services.email_notification_service import email_notification_service
from ui_v2.auth import get_authenticated_user
from ui_v2.i18n import t
from ui_v2.state import get_current_project_id, set_current_page, set_current_project


def _enter_project(project_id: str):
    set_current_project(project_id)
    set_current_page("dashboard")
    st.session_state.pop("selected_extraction_id", None)
    st.session_state.pop("selected_artifact_id", None)


def _render_project_team(project_id: str, owner_user_id: str, current_user_id: str) -> None:
    st.markdown(f"#### {t('project_team')}")
    st.caption(t("team_caption"))
    is_owner = owner_user_id == current_user_id

    if is_owner:
        with st.form(f"project_member_add_{project_id}", clear_on_submit=True):
            email = st.text_input(t("member_email"), key=f"project_member_email_{project_id}")
            add = st.form_submit_button(t("add_member"), type="primary")
        if add:
            account = user_repository.get_by_email(email)
            try:
                workspace_repository.add_member(
                    project_id,
                    current_user_id,
                    email=email,
                    user_id=account["id"] if account else None,
                    name=account.get("name", "") if account else "",
                )
                project = workspace_repository.get_project(project_id, current_user_id)
                inviter = get_authenticated_user() or {}
                base_url = os.getenv("APP_BASE_URL", "http://localhost:8501").rstrip("/")
                sent = email_notification_service.send_project_invitation(
                    recipient=str(email).strip().lower(),
                    inviter_name=str(inviter.get("name") or inviter.get("email") or ""),
                    project_name=str(project.get("name") or "Project Brain"),
                    invitation_url=base_url,
                )
                if not sent:
                    st.warning(t("member_added_email_failed"))
                    return
                st.success(t("member_added_email_sent"))
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

    members = workspace_repository.list_members(project_id, current_user_id)
    for member in members:
        member_status = (
            t("member_pending") if not member.get("user_id")
            else t("member_active") if member["status"] == "active"
            else t("member_blocked")
        )
        info_col, status_col, action_col = st.columns([0.50, 0.22, 0.28], vertical_alignment="center")
        with info_col:
            display_name = member.get("name") or member["email"]
            st.markdown(
                f'<div class="pb-member-name">{escape(display_name)}</div>'
                f'<div class="pb-member-meta">{escape(member["email"])} · {t(member["role"])}</div>',
                unsafe_allow_html=True,
            )
        with status_col:
            st.markdown(
                f'<span class="pb-member-status">{member_status}</span>',
                unsafe_allow_html=True,
            )
        with action_col:
            if is_owner and member["role"] != "owner":
                button_col, remove_col = st.columns(2)
                with button_col:
                    target_status = "blocked" if member["status"] == "active" else "active"
                    label = t("block_access") if target_status == "blocked" else t("restore_access")
                    if st.button(label, key=f"member_status_{member['id']}", width="stretch"):
                        workspace_repository.set_member_status(
                            project_id, current_user_id, member["id"], target_status
                        )
                        st.success(t("access_updated"))
                        st.rerun()
                with remove_col:
                    if st.button(t("delete"), key=f"member_remove_{member['id']}", width="stretch"):
                        workspace_repository.remove_member(project_id, current_user_id, member["id"])
                        st.success(t("member_removed"))
                        st.rerun()

    if not is_owner:
        st.info(t("owner_only"))


def render_projects():
    user = get_authenticated_user() or {}
    user_id = user["id"]
    st.title(t("projects"))
    st.caption(t("projects_caption"))

    with st.form("projects_create_form", clear_on_submit=True):
        col_name, col_action = st.columns([0.72, 0.28])
        with col_name:
            name = st.text_input(t("new_project"), placeholder=t("project_name"))
        with col_action:
            st.write("")
            st.write("")
            create = st.form_submit_button(t("create_project"), type="primary", width="stretch")
        if create:
            try:
                project = workspace_repository.create_project(
                    name, user_id, user.get("email", ""), user.get("name", "")
                )
                _enter_project(project["id"])
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

    projects = workspace_repository.list_projects(user_id)
    current_id = get_current_project_id()
    st.subheader(t("project_list"))

    st.markdown(
        f"""
        <div class="pb-project-table">
            <div class="pb-project-table-head">
                <span>{t('project')}</span><span>{t('sources')}</span><span>{t('artifacts')}</span>
                <span>{t('knowledge')}</span><span>{t('actions')}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for project in projects:
        project_id = project["id"]
        metrics = workspace_repository.dashboard_metrics(project_id)
        with st.container(key=f"pb_project_row_{project_id}"):
            name_col, sources_col, artifacts_col, knowledge_col, action_col = st.columns(
                [2.2, 0.75, 0.75, 0.75, 1.0], vertical_alignment="center"
            )
            with name_col:
                badge = f'<span class="pb-current-badge">{t("current")}</span>' if project_id == current_id else ""
                st.markdown(
                    f'<div class="pb-table-project-name">{escape(project["name"])}{badge}</div>',
                    unsafe_allow_html=True,
                )
            with sources_col:
                st.markdown(f'<div class="pb-table-cell">{metrics["sources"]}</div>', unsafe_allow_html=True)
            with artifacts_col:
                st.markdown(f'<div class="pb-table-cell">{metrics["artifacts"]}</div>', unsafe_allow_html=True)
            with knowledge_col:
                st.markdown(f'<div class="pb-table-cell">{metrics["knowledge_health"]}%</div>', unsafe_allow_html=True)
            with action_col:
                open_col, settings_col = st.columns([0.72, 0.28], gap="small", vertical_alignment="center")
                with open_col:
                    if st.button(
                        t("open") if project_id != current_id else t("opened"),
                        key=f"project_enter_{project_id}",
                        type="primary" if project_id != current_id else "secondary",
                        width="stretch", disabled=project_id == current_id,
                    ):
                        _enter_project(project_id)
                        st.rerun()
                with settings_col:
                    if st.button(
                        " ", key=f"project_settings_{project_id}",
                        help=t("settings"), width="stretch", icon=":material/settings:",
                    ):
                        set_current_project(project_id)
                        set_current_page("settings")
                        st.rerun()

            with st.expander(t("management"), expanded=False):
                is_owner = project["owner_user_id"] == user_id
                if is_owner:
                    with st.form(f"project_rename_form_{project_id}"):
                        renamed = st.text_input(
                            t("new_name"),
                            value=project["name"],
                            key=f"project_rename_value_{project_id}",
                        )
                        if st.form_submit_button(t("rename")):
                            workspace_repository.rename_project(project_id, renamed, user_id)
                            st.rerun()

                    if len(projects) > 1:
                        confirmation = st.text_input(
                            t("delete_confirm"),
                            key=f"project_delete_confirmation_{project_id}",
                        )
                        if st.button(
                            t("delete_project"),
                            key=f"project_delete_{project_id}",
                            disabled=confirmation != t("delete_word"),
                        ):
                            fallback = next(item["id"] for item in projects if item["id"] != project_id)
                            workspace_repository.delete_project(project_id, user_id)
                            if current_id == project_id:
                                set_current_project(fallback)
                            st.rerun()
                    else:
                        st.caption(t("only_project"))
                else:
                    st.info(t("owner_only"))

                st.divider()
                _render_project_team(project_id, project["owner_user_id"], user_id)
