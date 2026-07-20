from __future__ import annotations

import streamlit as st

from repositories.user_repository import user_repository


LOCAL_USER_KEY = "project_brain_local_user"


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
        )
    return st.session_state.get(LOCAL_USER_KEY)


def get_authenticated_email() -> str | None:
    user = get_authenticated_user()
    return user.get("email") if user else None


def logout():
    if _oidc_is_logged_in():
        st.logout()
        return
    st.session_state.pop(LOCAL_USER_KEY, None)
    st.rerun()


def _provider_configured(provider: str) -> bool:
    try:
        auth = st.secrets.get("auth", {})
        provider_config = auth.get(provider, {})
        return all(provider_config.get(key) for key in ("client_id", "client_secret", "server_metadata_url"))
    except Exception:
        return False


def _render_email_login():
    with st.form("email_login_form"):
        email = st.text_input("Email", key="auth_login_email")
        password = st.text_input("Пароль", type="password", key="auth_login_password")
        submitted = st.form_submit_button("Войти", type="primary", width="stretch")
    if submitted:
        user = user_repository.authenticate(email, password)
        if not user:
            st.error("Неверный email или пароль.")
            return
        st.session_state[LOCAL_USER_KEY] = user
        st.rerun()


def _render_email_registration():
    with st.form("email_registration_form"):
        name = st.text_input("Имя", key="auth_register_name")
        email = st.text_input("Email", key="auth_register_email")
        password = st.text_input("Пароль", type="password", key="auth_register_password")
        confirmation = st.text_input("Повторите пароль", type="password", key="auth_register_confirmation")
        submitted = st.form_submit_button("Зарегистрироваться", type="primary", width="stretch")
    if submitted:
        if password != confirmation:
            st.error("Пароли не совпадают.")
            return
        try:
            user = user_repository.register(email=email, password=password, name=name)
        except ValueError as exc:
            st.error(str(exc))
            return
        st.session_state[LOCAL_USER_KEY] = user
        st.rerun()


def render_auth_gate() -> bool:
    if get_authenticated_user():
        return True

    left, center, right = st.columns([0.28, 0.44, 0.28])
    with center:
        st.markdown(
            """
            <div class="pb-auth-heading">
                <div class="pb-brand-mark">PB</div>
                <h1>Project Brain</h1>
                <p>Войдите или создайте аккаунт</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        login_tab, registration_tab = st.tabs(["Вход", "Регистрация"])
        with login_tab:
            _render_email_login()
        with registration_tab:
            _render_email_registration()

        st.markdown('<div class="pb-auth-separator"><span>или</span></div>', unsafe_allow_html=True)
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
            st.caption("Социальный вход станет доступен после добавления OAuth/OIDC-ключей в секреты приложения.")
    return False
