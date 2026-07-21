from __future__ import annotations

from contextlib import contextmanager
from html import escape
from textwrap import dedent
import time

import streamlit as st

from ui_v2.assets import favicon_data_uri, logo_data_uri
from ui_v2.i18n import t


def render_intro_loader(duration: float = 3.55) -> None:
    placeholder = st.empty()
    placeholder.markdown(
        f"""
        <div class="pb-glass-loader">
            <div class="pb-loader-card">
                <div class="pb-loader-mark">
                    <div class="pb-loader-logo">
                        <img src="{logo_data_uri()}" alt="Project Brain">
                        <span class="pb-loader-trace"></span>
                    </div>
                </div>
                <div class="pb-loader-messages">
                    <span>{t('loader_message_1')}</span>
                    <span>{t('loader_message_2')}</span>
                    <span>{t('loader_message_3')}</span>
                    <span>{t('loader_message_4')}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    time.sleep(duration)
    placeholder.empty()


def render_transition_loader() -> None:
    placeholder = st.empty()
    placeholder.markdown(
        '<div class="pb-route-loader"><span></span><span></span><span></span></div>',
        unsafe_allow_html=True,
    )
    time.sleep(0.22)
    placeholder.empty()


@contextmanager
def inline_seal_loader(message: str):
    """Show the Project Brain seal crawling along an indeterminate task bar."""
    placeholder = st.empty()
    seal = favicon_data_uri()
    placeholder.markdown(
        dedent(f"""
        <div class="pb-inline-task-loader" role="status" aria-live="polite">
            <div class="pb-inline-task-track">
                <span class="pb-inline-task-seal"
                    style="-webkit-mask-image:url('{seal}');mask-image:url('{seal}')"></span>
            </div>
            <div class="pb-inline-task-label">{escape(str(message))}</div>
        </div>
        """).strip(),
        unsafe_allow_html=True,
    )
    try:
        yield
    finally:
        placeholder.empty()


def render_seal_progress(progress: float, message: str = "") -> None:
    """Render determinate source-processing progress with the seal as marker."""
    percentage = max(0, min(100, round(float(progress or 0) * 100)))
    seal = favicon_data_uri()
    label = escape(str(message).strip())
    st.markdown(
        dedent(f"""
        <div class="pb-source-task-loader" style="--pb-progress:{percentage}%"
             role="progressbar" aria-valuemin="0" aria-valuemax="100"
             aria-valuenow="{percentage}">
            <div class="pb-source-progress-track">
                <span class="pb-source-progress-fill"></span>
                <span class="pb-source-progress-seal"
                    style="-webkit-mask-image:url('{seal}');mask-image:url('{seal}')"></span>
            </div>
            <div class="pb-source-progress-copy">
                <span>{label}</span><strong>{percentage}%</strong>
            </div>
        </div>
        """).strip(),
        unsafe_allow_html=True,
    )
