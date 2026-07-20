import streamlit as st


DEFAULT_PAGE = "dashboard"
DEFAULT_PROJECT = "default"
DEFAULT_SOURCE = "meetings"
DEFAULT_DASHBOARD_LOADER = None
DEFAULT_CHAT_ARTIFACT = None


def get_current_page() -> str:
    if "ui_v2_page" not in st.session_state:
        st.session_state.ui_v2_page = DEFAULT_PAGE
    return st.session_state.ui_v2_page


def set_current_page(page: str):
    st.session_state.ui_v2_page = page


def get_current_project_id() -> str:
    if "ui_v2_project" not in st.session_state:
        st.session_state.ui_v2_project = DEFAULT_PROJECT
    project_id = st.session_state.ui_v2_project
    from repositories.workspace_repository import workspace_repository
    if not workspace_repository.get_project(project_id):
        project_id = DEFAULT_PROJECT
        st.session_state.ui_v2_project = project_id
    return project_id


def get_current_project() -> str:
    return get_current_project_id()


def set_current_project(project: str):
    st.session_state.ui_v2_project = project


def get_selected_source() -> str:
    if "ui_v2_selected_source" not in st.session_state:
        st.session_state.ui_v2_selected_source = DEFAULT_SOURCE
    return st.session_state.ui_v2_selected_source


def set_selected_source(source: str):
    st.session_state.ui_v2_selected_source = source


def open_source(source: str):
    set_selected_source(source)
    set_current_page("sources")


def get_dashboard_loader() -> str | None:
    if "ui_v2_dashboard_loader" not in st.session_state:
        st.session_state.ui_v2_dashboard_loader = DEFAULT_DASHBOARD_LOADER
    return st.session_state.ui_v2_dashboard_loader


def set_dashboard_loader(loader: str | None):
    st.session_state.ui_v2_dashboard_loader = loader


def get_chat_artifact() -> str | None:
    if "ui_v2_chat_artifact" not in st.session_state:
        st.session_state.ui_v2_chat_artifact = DEFAULT_CHAT_ARTIFACT
    return st.session_state.ui_v2_chat_artifact


def set_chat_artifact(artifact: str | None):
    st.session_state.ui_v2_chat_artifact = artifact


# Compatibility aliases for previous UI v2 files
def get_page() -> str:
    return get_current_page()


def set_page(page: str):
    set_current_page(page)


def get_project() -> str:
    return get_current_project_id()


def set_project(project: str):
    set_current_project(project)


def get_selected_extraction_id() -> str | None:
    return st.session_state.get("selected_extraction_id")


def set_selected_extraction_id(extraction_id: str | None):
    if extraction_id:
        st.session_state["selected_extraction_id"] = extraction_id
    else:
        st.session_state.pop("selected_extraction_id", None)


def open_artifacts(extraction_id: str | None = None):
    if extraction_id:
        set_selected_extraction_id(extraction_id)
    set_current_page("artifacts")
