import streamlit as st

from ui_v2.adapters.project_model_adapters import PROJECT_MODEL_TABS
from ui_v2.components.html import title
from ui_v2.i18n import t
from ui_v2.state import set_current_page


def render_project_model(memory_repository):
    if st.button(t("back"), key="project_model_back_to_settings", icon=":material/arrow_back:"):
        set_current_page("settings")
        st.rerun()
    title(f"{t('project_model')} · Beta", t("project_model_caption"))
    st.info(t("project_model_info"))

    tabs = st.tabs([tab["label"] for tab in PROJECT_MODEL_TABS])

    for tab, config in zip(tabs, PROJECT_MODEL_TABS):
        with tab:
            config["render"](memory_repository)
