from __future__ import annotations
import streamlit as st
from repositories.extraction_repository import extraction_repository
from services.artifact_api import artifact_api
from services.artifact_registry_v2 import get_artifact_meta, sort_artifacts
from ui.artifacts.artifact_download_center import render_artifact_download_center
from ui.artifacts.artifact_metadata_panel import render_artifact_metadata_panel
from ui.artifacts.artifact_navigation import render_artifact_breadcrumbs
from ui.artifacts.artifact_viewer_framework import render_artifact_viewer
from ui_v2.i18n import t


def _css_content(value: str) -> str:
    return (
        str(value or "")
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("<", "\\3C ")
        .replace(">", "\\3E ")
        .replace("\n", " ")
    )


def _render_artifact_tabs(extraction: dict, artifacts: list[dict]):
    artifacts = sort_artifacts(artifacts)
    if not artifacts:
        st.info(t("no_artifact_matches"))
        return

    labels = []
    used_labels = {}
    for artifact in artifacts:
        meta = get_artifact_meta(artifact.get("artifact_type", ""))
        base_label = f"{meta.icon} {meta.title}"
        used_labels[base_label] = used_labels.get(base_label, 0) + 1
        suffix = f" · {used_labels[base_label]}" if used_labels[base_label] > 1 else ""
        labels.append(base_label + suffix)

    tabs_key = f"artifact_tabs_{extraction['id'].replace('-', '_')}"
    tooltip_rules = []
    for index, artifact in enumerate(artifacts, start=1):
        meta = get_artifact_meta(artifact.get("artifact_type", ""))
        description = artifact.get("description") or meta.description or artifact.get("title")
        tooltip_rules.append(
            f"""
            .st-key-{tabs_key} [role="tab"]:nth-of-type({index}):hover::after {{
                content: "{_css_content(description)}";
            }}
            """
        )
    st.markdown(
        f"""
        <style>
            .st-key-{tabs_key} [role="tab"] {{
                position: relative;
            }}
            .st-key-{tabs_key} [role="tab"]:hover::after {{
                position: absolute;
                z-index: 1000;
                left: 0;
                top: calc(100% + 8px);
                width: max-content;
                max-width: 320px;
                padding: 7px 9px;
                border: 1px solid #3F3F46;
                border-radius: 8px;
                background: #18181B;
                color: #E4E4E7;
                font-size: 0.72rem;
                font-weight: 400;
                line-height: 1.35;
                text-align: left;
                white-space: normal;
                box-shadow: 0 8px 24px rgba(0,0,0,0.38);
                pointer-events: none;
            }}
            {''.join(tooltip_rules)}
        </style>
        """,
        unsafe_allow_html=True,
    )

    tabs = st.tabs(labels, key=tabs_key)
    for tab, artifact in zip(tabs, artifacts):
        with tab:
            render_artifact_viewer(artifact)
            render_artifact_metadata_panel(artifact)
            render_artifact_download_center(artifact)

def render_artifact_framework(project_id: str = "default"):
    st.header(t("artifacts"))
    extractions = extraction_repository.list(project_id=project_id, limit=100)
    if not extractions:
        st.info(t("no_extractions"))
        return

    selected_extraction_id = st.session_state.get("selected_extraction_id")
    default_index = 0
    if selected_extraction_id:
        for idx, item in enumerate(extractions):
            if item.get("id") == selected_extraction_id:
                default_index = idx
                break

    extraction = st.selectbox(
        t("extraction"),
        extractions,
        index=default_index,
        format_func=lambda e: f"{e['source_name']} · {e['status']} · {e['started_at']}",
    )
    st.session_state["selected_extraction_id"] = extraction["id"]
    render_artifact_breadcrumbs(extraction=extraction)

    query = st.text_input(t("search_artifacts"))
    artifacts = artifact_api.search_artifacts(extraction["id"], query) if query else artifact_api.list_artifacts(extraction["id"])

    _render_artifact_tabs(extraction, artifacts)
