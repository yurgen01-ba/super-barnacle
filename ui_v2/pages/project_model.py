import streamlit as st

from ui_v2.adapters.project_model_adapters import PROJECT_MODEL_TABS
from ui_v2.components.html import title


def render_project_model(memory_repository):
    title("Project Model · Beta", "Внутренняя модель проекта для advanced/debug usage")
    st.info("Этот раздел специально сделан малозаметным. Он нужен для проверки внутренних данных модели проекта.")

    tabs = st.tabs([tab["label"] for tab in PROJECT_MODEL_TABS])

    for tab, config in zip(tabs, PROJECT_MODEL_TABS):
        with tab:
            config["render"](memory_repository)
