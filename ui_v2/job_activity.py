from __future__ import annotations

from html import escape
from textwrap import dedent

import streamlit as st

from jobs.running_job_store import running_job_store
from ui_v2.assets import favicon_data_uri
from ui_v2.i18n import get_language


_SOURCE_LABELS = {
    "ru": {
        "meetings": "Встречи",
        "jira": "Jira",
        "confluence": "Confluence",
        "slack": "Slack",
        "files": "Файлы",
        "other": "Источник",
        "processing": "Идёт обработка источника",
    },
    "en": {
        "meetings": "Meetings",
        "jira": "Jira",
        "confluence": "Confluence",
        "slack": "Slack",
        "files": "Files",
        "other": "Source",
        "processing": "Processing source",
    },
    "uk": {
        "meetings": "Зустрічі",
        "jira": "Jira",
        "confluence": "Confluence",
        "slack": "Slack",
        "files": "Файли",
        "other": "Джерело",
        "processing": "Триває обробка джерела",
    },
}


def _source_section(job) -> str:
    metadata = job.metadata or {}
    explicit = str(metadata.get("source_section") or "").lower()
    if explicit:
        return explicit
    source = str(metadata.get("source") or "").lower()
    if "meeting" in source:
        return "meetings"
    if "confluence" in source:
        return "confluence"
    if "jira" in source:
        return "jira"
    if "slack" in source:
        return "slack"
    if "file" in source:
        return "files"
    return "other"


def _render_active_job_activity(project_id: str) -> None:
    active_jobs = [
        job
        for job in running_job_store.list(active_only=True)
        if str((job.metadata or {}).get("project_id", "default")) == str(project_id)
    ]
    if not active_jobs:
        return

    language = get_language()
    labels = _SOURCE_LABELS.get(language, _SOURCE_LABELS["en"])
    logo = favicon_data_uri()
    cards = []
    for job in reversed(active_jobs):
        source = _source_section(job)
        percentage = max(0, min(100, round(float(job.progress or 0) * 100)))
        source_label = labels.get(source, labels["other"])
        message = str(job.message or job.stage or "").strip()
        detail = f'<div class="pb-job-toast-detail">{escape(message)}</div>' if message else ""
        cards.append(
            dedent(f"""
            <div class="pb-job-toast" role="status" aria-live="polite">
              <div class="pb-job-progress" aria-hidden="true">
                <div class="pb-job-seal">
                  <span class="pb-job-seal-base" style="-webkit-mask-image:url('{logo}');mask-image:url('{logo}')"></span>
                  <span class="pb-job-seal-progress" style="--job-progress:{percentage}%;-webkit-mask-image:url('{logo}');mask-image:url('{logo}')"></span>
                </div>
                <strong>{percentage}%</strong>
              </div>
              <div class="pb-job-toast-copy">
                <div>{escape(labels['processing'])}</div>
                <b>{escape(source_label)}</b>
                {detail}
              </div>
            </div>
            """).strip()
        )

    html = dedent("""
        <style>
          .pb-job-toast-stack {
            position: fixed;
            right: 16px;
            bottom: 16px;
            z-index: 999990;
            display: flex;
            flex-direction: column;
            gap: 8px;
            width: min(320px, calc(100vw - 24px));
            pointer-events: none;
          }
          .pb-job-toast {
            display: flex;
            align-items: center;
            gap: 11px;
            min-height: 68px;
            padding: 9px 12px;
            border: 1px solid color-mix(in srgb, var(--pb-text, #e5e7eb) 14%, transparent);
            border-radius: 15px;
            color: var(--pb-text, #e5e7eb);
            background: color-mix(in srgb, var(--pb-panel, #111318) 88%, transparent);
            box-shadow: 0 18px 48px rgba(0,0,0,.24);
            backdrop-filter: blur(18px) saturate(145%);
            -webkit-backdrop-filter: blur(18px) saturate(145%);
          }
          .pb-job-progress {
            flex: 0 0 48px;
            width: 48px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 1px;
          }
          .pb-job-seal {
            position: relative;
            width: 44px;
            height: 34px;
          }
          .pb-job-seal > span {
            position: absolute;
            inset: 0;
            -webkit-mask-repeat: no-repeat;
            mask-repeat: no-repeat;
            -webkit-mask-position: center;
            mask-position: center;
            -webkit-mask-size: contain;
            mask-size: contain;
          }
          .pb-job-seal-base { background: currentColor; opacity: .16; }
          .pb-job-seal-progress {
            background: linear-gradient(90deg, #ff7777, #ff3f4a 55%, #d71935);
            clip-path: inset(calc(100% - var(--job-progress)) 0 0 0);
            transition: clip-path .45s ease;
          }
          .pb-job-progress strong {
            font-size: 10px;
            line-height: 1;
            color: var(--pb-text, #e5e7eb);
          }
          .pb-job-toast-copy { min-width: 0; font-size: 12px; line-height: 1.25; }
          .pb-job-toast-copy b { display: block; margin-top: 1px; font-size: 15px; }
          .pb-job-toast-detail {
            margin-top: 3px;
            overflow: hidden;
            color: var(--pb-muted, #9ca3af);
            font-size: 10px;
            text-overflow: ellipsis;
            white-space: nowrap;
          }
          @media (max-width: 720px) {
            .pb-job-toast-stack { right: 12px; bottom: 12px; }
          }
        </style>
        <div class="pb-job-toast-stack">
        """).strip() + "".join(cards) + "</div>"
    st.markdown(
        html,
        unsafe_allow_html=True,
    )


if hasattr(st, "fragment"):
    @st.fragment(run_every="1s")
    def render_active_job_activity(project_id: str) -> None:
        _render_active_job_activity(project_id)
else:
    def render_active_job_activity(project_id: str) -> None:
        _render_active_job_activity(project_id)
