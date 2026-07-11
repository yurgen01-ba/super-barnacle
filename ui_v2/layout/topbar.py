import streamlit as st

from ui_v2.state import get_project


def render_topbar():
    st.markdown(
        f"""
        <div class="pb-topbar">
            <div class="pb-row">
                <div>
                    <span class="pb-muted">Текущий проект</span>
                    <span style="margin-left:0.6rem;font-weight:700;color:white;">{get_project()} ▾</span>
                </div>
                <div style="display:flex;gap:1rem;align-items:center;">
                    <span class="pb-muted">Состояние знаний</span>
                    <span style="border:2px solid #3B82F6;border-radius:999px;padding:0.45rem 0.4rem;color:white;font-size:0.78rem;">91%</span>
                    <span><span style="color:#22C55E;">●</span> Здорово</span>
                    <span class="pb-muted">🔔</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
