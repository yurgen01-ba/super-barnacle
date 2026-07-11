import streamlit as st

from ui_v2.adapters.source_adapters import SOURCE_OPTIONS, render_source_adapter
from ui_v2.state import get_selected_source, set_selected_source


def render_sources(memory_repository):
    st.title("Sources")
    st.caption("Управление всеми источниками проекта")

    current = get_selected_source()
    labels = list(SOURCE_OPTIONS.values())
    keys = list(SOURCE_OPTIONS.keys())

    try:
        current_index = keys.index(current)
    except ValueError:
        current_index = 0

    selected_label = st.radio(
        "Source type",
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
