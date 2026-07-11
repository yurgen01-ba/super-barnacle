import streamlit as st

from ai.project_chat import answer_project_question
from repositories.chat_context_repository import ChatContextRepository


def _set_prompt(prompt: str):
    st.session_state.ui_v2_assistant_question = prompt


def render_assistant_panel():
    st.markdown(
        """
        <div class="pb-chat-card">
            <div style="font-size:1.25rem;font-weight:800;color:#FAFAFA;margin-bottom:0.25rem;">AI Assistant</div>
            <div class="pb-card-caption">Всегда доступен справа. Артефакты создаются из чата.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_chat, tab_artifacts = st.tabs(["Чат", "Артефакты"])

    with tab_chat:
        st.markdown(
            """
            <div class="pb-chat-bubble">
                Задавайте вопросы по проекту, анализируйте изменения или создавайте артефакты.
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Опиши проект OrgMeter", key="prompt_overview", width="stretch"):
            _set_prompt("Опиши проект OrgMeter вкратце")
            st.rerun()

        if st.button("Какие изменения были сегодня?", key="prompt_changes", width="stretch"):
            _set_prompt("Какие изменения были сегодня?")
            st.rerun()

        if st.button("Покажи процесс Funding", key="prompt_funding", width="stretch"):
            _set_prompt("Покажи процесс Funding")
            st.rerun()

        if st.button("Найди противоречия в правилах", key="prompt_contradictions", width="stretch"):
            _set_prompt("Найди противоречия в правилах")
            st.rerun()

        question = st.text_area(
            "Question",
            placeholder="Задайте вопрос...",
            height=110,
            label_visibility="collapsed",
            key="ui_v2_assistant_question",
        )

        if st.button("➤ Отправить", key="ui_v2_send", width="stretch", type="primary") and question.strip():
            with st.spinner("AI Analyst is reading Project Model..."):
                context = ChatContextRepository().search_context(question)
                answer = answer_project_question(question, context)
            st.markdown(answer)

    with tab_artifacts:
        st.caption("Пока это entry-points. Подключим существующие генераторы следующим шагом.")
        st.button("🎫 Jira tickets", key="artifact_jira", width="stretch", disabled=True)
        st.button("📄 Confluence article", key="artifact_confluence", width="stretch", disabled=True)
        st.button("🧪 Test cases", key="artifact_tests", width="stretch", disabled=True)
        st.markdown(
            "<div class='pb-nonfunctional'>Disabled = UI placeholder, backend not connected yet.</div>",
            unsafe_allow_html=True,
        )
