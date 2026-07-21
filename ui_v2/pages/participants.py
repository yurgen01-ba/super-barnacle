from __future__ import annotations

import streamlit as st

from repositories.participant_repository import participant_repository
from ui_v2.i18n import t
from ui_v2.state import get_current_project_id


def render_participants():
    project_id = get_current_project_id()
    st.title(t("participants"))
    st.caption(t("participants_caption"))
    participants = participant_repository.list_grouped(project_id)
    if not participants:
        st.info(t("participants_empty"))
        return
    participants = [
        {
            t("participant_name"): item["name"],
            t("role"): item["role"],
            t("sources"): item["sources"],
            t("last_updated"): item["updated_at"],
        }
        for item in participants
    ]
    st.dataframe(participants, width="stretch", hide_index=True)
    st.caption(t("participants_total", count=len(participants)))
