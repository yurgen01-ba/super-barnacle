from __future__ import annotations

import streamlit as st

from repositories.participant_repository import participant_repository
from ui_v2.i18n import t
from ui_v2.state import get_current_project_id


def render_participants():
    project_id = get_current_project_id()
    st.title(t("participants"))
    st.caption(
        "Участники встреч и люди, найденные в сообщениях Slack, Jira-тикетах "
        "и документах Confluence. Список пополняется при обработке источников."
    )
    participants = participant_repository.list_grouped(project_id)
    if not participants:
        st.info("Участники пока не найдены. Добавьте и обработайте источники проекта.")
        return
    st.dataframe(participants, width="stretch", hide_index=True)
    st.caption(f"Всего уникальных участников: {len(participants)}")
