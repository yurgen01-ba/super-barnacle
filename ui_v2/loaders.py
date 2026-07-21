from __future__ import annotations

from contextlib import contextmanager
from html import escape
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
        f"""
        <div class="pb-inline-task-loader" role="status" aria-live="polite">
            <div class="pb-inline-task-track">
                <span class="pb-inline-task-seal"
                    style="-webkit-mask-image:url('{seal}');mask-image:url('{seal}')"></span>
            </div>
            <div class="pb-inline-task-label">{escape(str(message))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    try:
        yield
    finally:
        placeholder.empty()
