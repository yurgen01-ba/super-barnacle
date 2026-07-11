from __future__ import annotations

from ui.job_status import render_job_status, render_latest_job_status


def render_job_status_v2(job_id: str | None):
    render_job_status(job_id)


def render_latest_job_status_v2(job_type: str):
    render_latest_job_status(job_type)
