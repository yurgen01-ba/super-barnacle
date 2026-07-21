from __future__ import annotations

from pathlib import Path

import streamlit as st

from repositories.user_repository import UserRepositoryError, user_repository
from ui_v2.assets import default_avatar_data_uri, file_data_uri
from ui_v2.auth import get_authenticated_user, logout, refresh_local_user
from ui_v2.i18n import t


AVATAR_DIR = Path("data/avatars")
MAX_AVATAR_BYTES = 2 * 1024 * 1024


def _error_text(exc: Exception) -> str:
    return t(exc.code, str(exc)) if isinstance(exc, UserRepositoryError) else str(exc)


def avatar_source(user: dict) -> str:
    avatar_url = str(user.get("avatar_url") or "")
    if avatar_url and Path(avatar_url).exists():
        return file_data_uri(avatar_url)
    if avatar_url.startswith(("https://", "http://", "data:")):
        return avatar_url
    return default_avatar_data_uri(user.get("name") or user.get("email") or "User")


def render_profile():
    user = get_authenticated_user() or {}
    if not user:
        st.warning(t("session_missing"))
        return

    st.title(t("profile"))
    avatar_col, details_col = st.columns([0.22, 0.78], vertical_alignment="center")
    with avatar_col:
        st.image(avatar_source(user), width=128)
    with details_col:
        st.subheader(user.get("name") or user.get("email"))
        st.caption(user.get("email", ""))
        provider = user.get("auth_provider", "email")
        st.caption(f"{t('authentication')}: {provider}")

    st.markdown(f"### {t('profile_title')}")
    with st.form("profile_details_form"):
        name = st.text_input(t("name"), value=user.get("name", ""))
        avatar = st.file_uploader(
            t("avatar"),
            type=["png", "jpg", "jpeg", "webp"],
            help="PNG, JPG или WebP, не более 2 МБ.",
        )
        save_profile = st.form_submit_button(t("save_profile"), type="primary")
    if save_profile:
        avatar_path = None
        if avatar is not None:
            payload = avatar.getvalue()
            if len(payload) > MAX_AVATAR_BYTES:
                st.error(t("avatar_too_large"))
                return
            AVATAR_DIR.mkdir(parents=True, exist_ok=True)
            suffix = Path(avatar.name).suffix.lower() or ".png"
            avatar_path = AVATAR_DIR / f"{user['id']}{suffix}"
            avatar_path.write_bytes(payload)
        try:
            updated = user_repository.update_profile(
                user["id"],
                name=name,
                avatar_url=str(avatar_path) if avatar_path else None,
            )
            refresh_local_user(user["id"])
            st.success(t("profile_saved"))
            st.rerun()
        except ValueError as exc:
            st.error(_error_text(exc))

    st.markdown(f"### {t('security')}")
    if user.get("auth_provider") == "email":
        with st.form("change_password_form"):
            current_password = st.text_input(t("current_password"), type="password")
            new_password = st.text_input(
                t("new_password"),
                type="password",
                placeholder="8+ chars: Aa, 1, !",
            )
            repeat_password = st.text_input(
                t("repeat_new_password"),
                type="password",
                placeholder="8+ chars: Aa, 1, !",
            )
            change_password = st.form_submit_button(t("change_password"), type="primary")
        if change_password:
            if new_password != repeat_password:
                st.error(t("passwords_mismatch"))
            else:
                try:
                    user_repository.change_password(user["id"], current_password, new_password)
                    st.success(t("password_changed"))
                except ValueError as exc:
                    st.error(_error_text(exc))
    else:
        st.info(t("oauth_password"))

    if st.button(t("logout"), key="profile_logout", type="primary"):
        logout()
