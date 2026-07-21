import streamlit as st

from ui_v2.adapters.source_adapters import render_source_adapter, source_options
from ui_v2.i18n import t
from ui_v2.state import get_selected_source, set_selected_source


def render_sources(memory_repository):
    st.title(t("sources"))
    st.caption(t("sources_caption"))

    current = get_selected_source()
    options = source_options()
    if current not in options:
        current = next(iter(options))
        set_selected_source(current)

    columns = st.columns(len(options))
    for column, (source_key, source_label) in zip(columns, options.items()):
        with column:
            if st.button(
                source_label,
                key=f"pb_source_card_{source_key}_sources",
                type="primary" if source_key == current else "secondary",
                width="stretch",
            ):
                set_selected_source(source_key)
                st.rerun()

    st.divider()
    render_source_adapter(current, memory_repository)
