from __future__ import annotations

import streamlit as st


def pb_card(title: str, body: str = "", footer: str = "", icon: str = ""):
    st.markdown(
        f"""
        <div class="pb-card">
            <div class="pb-card-title">{icon} {title}</div>
            <div class="pb-card-body">{body}</div>
            {f'<div class="pb-card-footer">{footer}</div>' if footer else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def pb_metric_card(title: str, value: str | int | float, delta: str = ""):
    st.markdown(
        f"""
        <div class="pb-metric-card">
            <div class="pb-metric-title">{title}</div>
            <div class="pb-metric-value">{value}</div>
            {f'<div class="pb-metric-delta">{delta}</div>' if delta else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def pb_status_badge(label: str, tone: str = "neutral"):
    st.markdown(
        f"<span class='pb-status-badge pb-status-{tone}'>{label}</span>",
        unsafe_allow_html=True,
    )


def pb_panel(title: str, caption: str = ""):
    st.markdown(
        f"""
        <div class="pb-panel">
            <div class="pb-panel-title">{title}</div>
            {f'<div class="pb-caption">{caption}</div>' if caption else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def pb_divider():
    st.markdown("<div class='pb-divider'></div>", unsafe_allow_html=True)
