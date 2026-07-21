import streamlit as st


DEFAULT_PAGE = "dashboard"
DEFAULT_PROJECT = "default"
DEFAULT_SOURCE = "meetings"
DEFAULT_DASHBOARD_LOADER = None
DEFAULT_CHAT_ARTIFACT = None
DISMISSED_JOB_RESULTS_KEY = "ui_v2_dismissed_job_results"


def dismiss_latest_source_job_result(project_id: str, source_section: str) -> None:
    """Hide the current terminal result after its loader has been closed."""
    if not project_id or not source_section:
        return

    from jobs.knowledge_extraction_service import KnowledgeExtractionJobService

    job = KnowledgeExtractionJobService().latest(
        active_only=False,
        project_id=project_id,
        source_section=source_section,
    )
    if not job or job.is_active():
        return

    dismissed = set(st.session_state.get(DISMISSED_JOB_RESULTS_KEY, []))
    dismissed.add(job.id)
    st.session_state[DISMISSED_JOB_RESULTS_KEY] = list(dismissed)


def is_job_result_dismissed(job_id: str) -> bool:
    return bool(job_id) and job_id in set(
        st.session_state.get(DISMISSED_JOB_RESULTS_KEY, [])
    )


def get_current_page() -> str:
    if "ui_v2_page" not in st.session_state:
        st.session_state.ui_v2_page = DEFAULT_PAGE
    return st.session_state.ui_v2_page


def set_current_page(page: str):
    if (
        st.session_state.get("ui_v2_page") == "sources"
        and page != "sources"
    ):
        dismiss_latest_source_job_result(
            get_current_project_id(),
            st.session_state.get("ui_v2_selected_source", DEFAULT_SOURCE),
        )
    st.session_state.ui_v2_page = page


def get_current_project_id() -> str:
    from repositories.workspace_repository import workspace_repository
    from ui_v2.auth import get_authenticated_user

    user = get_authenticated_user()
    if not user:
        return DEFAULT_PROJECT
    user_id = user["id"]
    projects = workspace_repository.list_projects(user_id)
    if "ui_v2_project" not in st.session_state:
        st.session_state.ui_v2_project = projects[0]["id"] if projects else DEFAULT_PROJECT
    project_id = st.session_state.ui_v2_project
    if not workspace_repository.get_project(project_id, user_id):
        projects = workspace_repository.list_projects(user_id)
        project_id = projects[0]["id"] if projects else DEFAULT_PROJECT
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
    previous = st.session_state.get("ui_v2_selected_source")
    if previous and previous != source:
        dismiss_latest_source_job_result(get_current_project_id(), previous)
    st.session_state.ui_v2_selected_source = source


def open_source(source: str):
    set_selected_source(source)
    set_current_page("sources")


def open_connection_settings(provider: str):
    provider = str(provider or "").lower()
    if provider not in {"jira", "confluence", "slack"}:
        raise ValueError("Unsupported connection settings section")
    st.session_state.ui_v2_connection_settings = provider
    st.session_state.connection_settings_selector = provider
    set_current_page("settings")


def get_connection_settings() -> str:
    provider = str(st.session_state.get("ui_v2_connection_settings", "jira")).lower()
    return provider if provider in {"jira", "confluence", "slack"} else "jira"


def set_connection_settings(provider: str):
    provider = str(provider or "").lower()
    if provider not in {"jira", "confluence", "slack"}:
        raise ValueError("Unsupported connection settings section")
    st.session_state.ui_v2_connection_settings = provider


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
