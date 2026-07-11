import streamlit as st

from config_pkg.settings import settings


def render_header():
    st.title("🧠 Project Brain 3.0")
    st.caption("Turn project sources into structured memory and delivery-ready artifacts.")
    st.caption(f"Version: {settings.app_version} | SQLite DB: {settings.db_path}")

