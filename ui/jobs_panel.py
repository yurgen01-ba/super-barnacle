from __future__ import annotations

import streamlit as st

from jobs.job_registry import JobRegistry
from ui.job_status import render_job_status


def render_jobs_panel():
    registry = JobRegistry()
    jobs = registry.list_all()

    if not jobs:
        st.info("No background jobs.")
        return

    for job in jobs:
        with st.expander(f"{job.job_type} · {job.status} · {job.id[:8]}", expanded=job.is_active()):
            render_job_status(job.id)
