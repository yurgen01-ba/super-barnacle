from __future__ import annotations

import json

import streamlit as st

from repositories.artifact_repository import artifact_repository
from ui_v2.state import get_current_project_id


def _download_payload(artifact: dict) -> tuple[str, str, str]:
    fmt = str(artifact.get("format") or "text").lower()
    extension = {"markdown": "md", "json": "json", "html": "html"}.get(fmt, "txt")
    mime = {
        "md": "text/markdown",
        "json": "application/json",
        "html": "text/html",
        "txt": "text/plain",
    }[extension]
    content = artifact.get("content") or ""
    if extension == "json":
        try:
            content = json.dumps(json.loads(content), ensure_ascii=False, indent=2)
        except Exception:
            pass
    safe_title = "".join(ch if ch.isalnum() else "_" for ch in artifact.get("title", "artifact"))[:80]
    return content, f"{safe_title}.{extension}", mime


def render_exports():
    project_id = get_current_project_id()
    artifacts = artifact_repository.list_user_generated_by_project(project_id)

    st.title("Экспорт данных")
    st.caption(
        "Готовые документы, Jira-задачи, презентации и другие результаты, "
        "которые пользователь запросил у AI."
    )

    if not artifacts:
        st.info(
            "Пользовательских AI-артефактов пока нет. Создайте документ, Jira-задачи "
            "или другой результат во вкладке «Артефакты» справа."
        )
        return

    query = st.text_input("Поиск", placeholder="Название или тип артефакта")
    if query.strip():
        needle = query.strip().lower()
        artifacts = [
            item for item in artifacts
            if needle in str(item.get("title", "")).lower()
            or needle in str(item.get("artifact_type", "")).lower()
        ]

    st.caption(f"Найдено: {len(artifacts)}")
    for artifact in artifacts:
        with st.container(border=True):
            info_col, download_col, delete_col = st.columns([0.60, 0.22, 0.18])
            with info_col:
                st.markdown(f"**{artifact['title']}**")
                st.caption(
                    f"{artifact['artifact_type']} · {artifact.get('format') or 'text'} · "
                    f"{str(artifact.get('created_at') or '')[:16]}"
                )
            payload, filename, mime = _download_payload(artifact)
            with download_col:
                st.download_button(
                    "Скачать",
                    data=payload,
                    file_name=filename,
                    mime=mime,
                    key=f"export_download_{artifact['id']}",
                    width="stretch",
                )
            with delete_col:
                if st.button(
                    "Удалить",
                    key=f"export_delete_{artifact['id']}",
                    width="stretch",
                ):
                    artifact_repository.delete(artifact["id"], project_id)
                    st.rerun()
