from __future__ import annotations

import streamlit as st


LANGUAGE_LABELS = {"ru": "RU", "en": "EN", "uk": "UK"}

TRANSLATIONS = {
    "ru": {
        "projects": "Проекты",
        "workspace": "Рабочее пространство",
        "sources": "Источники",
        "speech_quality": "Качество речи",
        "artifacts": "Артефакты",
        "exports": "Экспорт данных",
        "source_section": "ИСТОЧНИКИ",
        "project_section": "ПРОЕКТ",
        "meetings": "Встречи",
        "files": "Файлы",
        "settings": "Настройки",
        "project_model": "Модель проекта",
        "participants": "Участники",
        "project": "Проект",
        "knowledge_health": "Состояние знаний",
        "logout": "Выйти",
        "profile": "Личный кабинет",
        "login_intro": "Войдите или создайте аккаунт",
        "login": "Вход",
        "registration": "Регистрация",
        "password": "Пароль",
        "repeat_password": "Повторите пароль",
        "name": "Имя",
        "sign_in": "Войти",
        "sign_up": "Зарегистрироваться",
        "or": "или",
        "language": "Язык",
        "theme": "Тема",
        "sources_caption": "Управление всеми источниками проекта",
    },
    "en": {
        "projects": "Projects",
        "workspace": "Workspace",
        "sources": "Sources",
        "speech_quality": "Speech quality",
        "artifacts": "Artifacts",
        "exports": "Data export",
        "source_section": "SOURCES",
        "project_section": "PROJECT",
        "meetings": "Meetings",
        "files": "Files",
        "settings": "Settings",
        "project_model": "Project model",
        "participants": "Participants",
        "project": "Project",
        "knowledge_health": "Knowledge health",
        "logout": "Log out",
        "profile": "Profile",
        "login_intro": "Sign in or create an account",
        "login": "Sign in",
        "registration": "Registration",
        "password": "Password",
        "repeat_password": "Repeat password",
        "name": "Name",
        "sign_in": "Sign in",
        "sign_up": "Create account",
        "or": "or",
        "language": "Language",
        "theme": "Theme",
        "sources_caption": "Manage all project data sources",
    },
    "uk": {
        "projects": "Проєкти",
        "workspace": "Робочий простір",
        "sources": "Джерела",
        "speech_quality": "Якість мовлення",
        "artifacts": "Артефакти",
        "exports": "Експорт даних",
        "source_section": "ДЖЕРЕЛА",
        "project_section": "ПРОЄКТ",
        "meetings": "Зустрічі",
        "files": "Файли",
        "settings": "Налаштування",
        "project_model": "Модель проєкту",
        "participants": "Учасники",
        "project": "Проєкт",
        "knowledge_health": "Стан знань",
        "logout": "Вийти",
        "profile": "Особистий кабінет",
        "login_intro": "Увійдіть або створіть обліковий запис",
        "login": "Вхід",
        "registration": "Реєстрація",
        "password": "Пароль",
        "repeat_password": "Повторіть пароль",
        "name": "Ім’я",
        "sign_in": "Увійти",
        "sign_up": "Зареєструватися",
        "or": "або",
        "language": "Мова",
        "theme": "Тема",
        "sources_caption": "Керування всіма джерелами даних проєкту",
    },
}


def _browser_language() -> str:
    try:
        locale = str(getattr(st.context, "locale", "") or "").lower()
    except Exception:
        locale = ""
    code = locale.split("-", 1)[0].split("_", 1)[0]
    return code if code in TRANSLATIONS else "en"


def get_language() -> str:
    if "pb_language" not in st.session_state:
        st.session_state.pb_language = _browser_language()
    return st.session_state.pb_language


def set_language(language: str) -> None:
    if language in TRANSLATIONS:
        st.session_state.pb_language = language


def t(key: str, default: str | None = None) -> str:
    language = get_language()
    return TRANSLATIONS.get(language, TRANSLATIONS["en"]).get(
        key,
        TRANSLATIONS["en"].get(key, default or key),
    )
