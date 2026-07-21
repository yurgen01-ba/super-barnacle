from __future__ import annotations

import streamlit as st

from repositories.participant_repository import participant_repository
from ui_v2.i18n import t
from ui_v2.state import get_current_project_id


def render_participants():
    project_id = get_current_project_id()
    st.title(t("participants"))
    st.caption(t("participants_caption"))
    meeting_speakers = participant_repository.list_meeting_speakers(project_id)
    if meeting_speakers:
        with st.expander(t("edit_participant_names"), expanded=False):
            for item in meeting_speakers:
                label_col, input_col, save_col = st.columns(
                    [0.28, 0.52, 0.20], vertical_alignment="center"
                )
                with label_col:
                    st.caption(f"{item['source_ref']} · {item['role']}")
                with input_col:
                    edited_name = st.text_input(
                        t("participant_name"), value=item["name"],
                        key=f"participant_edit_{item['id']}", label_visibility="collapsed",
                    )
                with save_col:
                    if st.button(t("save"), key=f"participant_save_{item['id']}"):
                        participant_repository.set_meeting_speaker_name(
                            project_id=project_id, source_ref=item["source_ref"],
                            speaker=item["role"], name=edited_name,
                        )
                        st.success(t("participant_names_saved"))
                        st.rerun()

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
