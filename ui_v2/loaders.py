from __future__ import annotations

import time

import streamlit as st

from ui_v2.assets import logo_data_uri
from ui_v2.i18n import t


def render_intro_loader() -> None:
    placeholder = st.empty()
    placeholder.markdown(
        f"""
        <div class="pb-glass-loader">
            <div class="pb-loader-card">
                <img src="{logo_data_uri()}" alt="Project Brain">
                <div class="pb-loader-orbit"></div>
                <div class="pb-loader-messages">
                    <span>{t('loader_message_1')}</span>
                    <span>{t('loader_message_2')}</span>
                    <span>{t('loader_message_3')}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    time.sleep(2.8)
    placeholder.empty()


def render_transition_loader() -> None:
    placeholder = st.empty()
    placeholder.markdown(
        '<div class="pb-route-loader"><span></span><span></span><span></span></div>',
        unsafe_allow_html=True,
    )
    time.sleep(0.22)
    placeholder.empty()
