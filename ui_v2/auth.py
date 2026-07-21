from __future__ import annotations

import os

import streamlit as st

from repositories.user_repository import UserRepositoryError, user_repository
from services.email_notification_service import email_notification_service
from ui_v2.i18n import t


LOCAL_USER_KEY = "project_brain_local_user"


def _error_text(exc: Exception) -> str:
    if isinstance(exc, UserRepositoryError):
        return t(exc.code, str(exc))
    return str(exc)


def _oidc_claim(name: str, default=None):
    try:
        return getattr(st.user, name, default)
    except Exception:
        return default


def _oidc_is_logged_in() -> bool:
    try:
        return bool(st.user.is_logged_in)
    except Exception:
        return False


def _oidc_provider() -> str:
    issuer = str(_oidc_claim("iss", "")).lower()
    subject = str(_oidc_claim("sub", "")).lower()
    if subject.startswith("facebook|"):
        return "facebook"
    if subject.startswith("google-oauth2|"):
        return "google"
    if "google" in issuer:
        return "google"
    if "facebook" in issuer or "meta" in issuer:
        return "facebook"
    return "oidc"


def get_authenticated_user() -> dict | None:
    if _oidc_is_logged_in():
        email = str(_oidc_claim("email", "") or "")
        if not email:
            return None
        return user_repository.upsert_oidc_user(
            email=email,
            name=str(_oidc_claim("name", "") or email),
            provider=_oidc_provider(),
            subject=str(_oidc_claim("sub", "") or email),
            avatar_url=str(_oidc_claim("picture", "") or "") or None,
        )
    return st.session_state.get(LOCAL_USER_KEY)


def get_authenticated_email() -> str | None:
    user = get_authenticated_user()
    return user.get("email") if user else None


def logout():
    st.session_state.pop("pb_intro_seen", None)
    st.session_state.pop("pb_preferences_user", None)
    if _oidc_is_logged_in():
        st.logout()
        return
    st.session_state.pop(LOCAL_USER_KEY, None)
    st.rerun()


def refresh_local_user(user_id: str) -> dict | None:
    user = user_repository.get_by_id(user_id)
    if user:
        st.session_state[LOCAL_USER_KEY] = user
    return user


def _provider_configured(provider: str) -> bool:
    try:
        auth = st.secrets.get("auth", {})
        provider_config = auth.get(provider, {})
        return all(provider_config.get(key) for key in ("client_id", "client_secret", "server_metadata_url"))
    except Exception:
        return False


def _render_email_login():
    with st.form("email_login_form"):
        email = st.text_input(t("email"), key="auth_login_email")
        password = st.text_input(
            t("password"),
            type="password",
            placeholder="••••••••",
            key="auth_login_password",
        )
        submitted = st.form_submit_button(t("sign_in"), type="primary", width="stretch")
    if submitted:
        try:
            user = user_repository.authenticate(email, password)
        except ValueError as exc:
            st.error(_error_text(exc))
            return
        if not user:
            st.error(t("invalid_credentials"))
            return
        st.session_state[LOCAL_USER_KEY] = user
        st.rerun()
    with st.expander(t("verification_missing"), expanded=False):
        resend_email = st.text_input(t("resend_email"), key="auth_resend_email")
        if st.button(t("resend"), key="auth_resend_button"):
            token = user_repository.create_verification_token(resend_email)
            user = user_repository.get_by_email(resend_email)
            if token and user:
                base_url = os.getenv("APP_BASE_URL", "http://localhost:8501").rstrip("/")
                try:
                    sent = email_notification_service.send_verification_email(
                        recipient=user["email"],
                        name=user["name"],
                        verification_url=f"{base_url}/?verify_token={token}",
                    )
                except Exception as exc:
                    st.error(f"Письмо не отправлено: {exc}")
                else:
                    if sent:
                        st.success(t("resend_sent"))
                    else:
                        st.error(t("smtp_missing"))
            else:
                st.info(t("resend_safe"))


def _render_email_registration():
    with st.form("email_registration_form"):
        name = st.text_input(t("name"), key="auth_register_name")
        email = st.text_input(t("email"), key="auth_register_email")
        password = st.text_input(
            t("password"),
            type="password",
            placeholder="8+ chars: Aa, 1, !",
            key="auth_register_password",
        )
        confirmation = st.text_input(
            t("repeat_password"),
            type="password",
            placeholder="8+ chars: Aa, 1, !",
            key="auth_register_confirmation",
        )
        st.caption(t("password_policy"))
        submitted = st.form_submit_button(t("sign_up"), type="primary", width="stretch")
    if submitted:
        if password != confirmation:
            st.error(t("passwords_mismatch"))
            return
        try:
            user = user_repository.register(email=email, password=password, name=name)
        except ValueError as exc:
            st.error(_error_text(exc))
            return
        token = user.pop("_verification_token")
        base_url = os.getenv("APP_BASE_URL", "http://localhost:8501").rstrip("/")
        verification_url = f"{base_url}/?verify_token={token}"
        try:
            sent = email_notification_service.send_verification_email(
                recipient=user["email"],
                name=user["name"],
                verification_url=verification_url,
            )
        except Exception as exc:
            st.error(f"Аккаунт создан, но письмо не отправлено: {exc}")
            return
        if sent:
            st.success(t("verify_check_mail"))
        else:
            st.error(t("smtp_missing"))


def _handle_email_verification() -> None:
    token = str(st.query_params.get("verify_token", "") or "")
    if not token:
        return
    verified = user_repository.verify_email(token)
    del st.query_params["verify_token"]
    if verified:
        st.success(t("verify_success"))
    else:
        st.error(t("verify_invalid"))


def render_auth_gate() -> bool:
    _handle_email_verification()
    if get_authenticated_user():
        return True

    left, center, right = st.columns([0.28, 0.44, 0.28])
    with center:
        st.markdown(
            f"""
            <div class="pb-auth-heading">
                <div class="pb-auth-logo" aria-label="Project Brain"></div>
                <h1>Project Brain</h1>
                <p>{t('login_intro')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        login_tab, registration_tab = st.tabs([t("login"), t("registration")])
        with login_tab:
            _render_email_login()
        with registration_tab:
            _render_email_registration()

        st.markdown(f'<div class="pb-auth-separator"><span>{t("or")}</span></div>', unsafe_allow_html=True)
        google_ready = _provider_configured("google")
        facebook_ready = _provider_configured("facebook")
        social_col1, social_col2 = st.columns(2)
        with social_col1:
            if st.button(
                "Google",
                key="auth_google",
                width="stretch",
                disabled=not google_ready,
                help=None if google_ready else "Добавьте настройки Google OIDC в secrets.toml",
            ):
                st.login("google")
        with social_col2:
            if st.button(
                "Facebook",
                key="auth_facebook",
                width="stretch",
                disabled=not facebook_ready,
                help=None if facebook_ready else "Подключите Facebook через OIDC-провайдер в secrets.toml",
            ):
                st.login("facebook")
        if not google_ready or not facebook_ready:
            st.caption(t("social_setup"))
    return False
