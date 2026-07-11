from __future__ import annotations

import streamlit as st

from ui.dark_theme import apply_complete_dark_theme


def apply_global_styles():
    apply_complete_dark_theme()


def render_section_title(title: str, caption: str | None = None):
    st.markdown(f"## {title}")
    if caption:
        st.caption(caption)


def render_card(title: str, body: str = "", badge: str | None = None):
    badge_html = f"<span class='pb-badge'>{badge}</span>" if badge else ""
    st.markdown(
        f"""
        <div class="pb-card">
            <div class="pb-card-title">{title} {badge_html}</div>
            <div class="pb-card-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
