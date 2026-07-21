import streamlit as st

from ui_v2.adapters.source_adapters import render_source_adapter, source_options
from ui_v2.i18n import t
from ui_v2.state import get_selected_source, set_selected_source


def render_sources(memory_repository):
    st.title(t("sources"))
    st.caption(t("sources_caption"))

    current = get_selected_source()
    SOURCE_OPTIONS = source_options()
    labels = list(SOURCE_OPTIONS.values())
    keys = list(SOURCE_OPTIONS.keys())

    try:
        current_index = keys.index(current)
    except ValueError:
        current_index = 0

    selected_label = st.radio(
        t("source_type"),
        labels,
        index=current_index,
        horizontal=True,
        label_visibility="collapsed",
        key="ui_v2_sources_radio",
    )

    selected_key = keys[labels.index(selected_label)]
    set_selected_source(selected_key)

    st.divider()
    render_source_adapter(selected_key, memory_repository)
