import streamlit as st

from memory.db import init_db
from memory.fact_schema import init_fact_schema
from repositories.memory_repository import MemoryRepository
from ui_v2.design import inject_ui_v2_theme
from ui_v2.layout.chat import render_chat_panel
from ui_v2.layout.menu import render_menu
from ui_v2.layout.topbar import render_topbar
from ui_v2.pages.page_registry import render_current_page


def render_app_shell_v2():
    st.set_page_config(
        page_title="Project Brain",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    inject_ui_v2_theme()

    init_db()
    init_fact_schema()

    memory_repository = MemoryRepository()

    menu_col, main_col, chat_col = st.columns([0.16, 0.60, 0.24], gap="large")

    with menu_col:
        render_menu()

    with main_col:
        render_topbar()
        render_current_page(memory_repository)

    with chat_col:
        render_chat_panel(memory_repository)
