from __future__ import annotations

import streamlit as st

from jobs.running_job import RunningJobStatus
from repositories.progress_repository import ProgressRepository


def _render_result_summary(result):
    if not result:
        return

    st.success("Job result is available.")

    if isinstance(result, dict) and result.get("extraction"):
        extraction = result["extraction"]
        st.success(
            f"Обработка завершена. Создано артефактов: {extraction.get('artifact_count', 0)}."
        )
        if st.button("Открыть полученные артефакты", key=f"open_artifacts_{extraction['id']}", type="primary"):
            st.session_state.ui_v2_page = "artifacts"
            st.session_state.selected_extraction_id = extraction["id"]
            st.rerun()
        return

    if isinstance(result, dict):
        if "save_result" in result:
            save_result = result.get("save_result", {})
            st.caption(
                f"Saved: {save_result.get('saved', 0)}, "
                f"skipped: {save_result.get('skipped', 0)}, "
                f"items: {save_result.get('items_count', 0)}"
            )

        if "results" in result:
            st.caption(f"Processed result groups: {len(result.get('results', []))}")

        with st.expander("Result details", expanded=False):
            st.write(result)
    else:
        with st.expander("Result details", expanded=False):
            st.write(result)


def _render_job_status_body(job_id: str | None):
    if not job_id:
        st.info("No running job.")
        return

    repository = ProgressRepository()
    job = repository.get(job_id)

    if not job:
        st.warning("Job not found.")
        return

    st.markdown(f"**Job:** `{job.job_type}`")
    st.markdown(f"**Status:** `{job.status}`")
    st.progress(float(job.progress or 0.0))

    if job.stage:
        st.caption(f"Stage: {job.stage}")

    if job.message:
        st.caption(job.message)

    if job.error:
        st.error(job.error)

    if job.logs:
        with st.expander("Job logs", expanded=False):
            for line in job.logs[-50:]:
                st.text(line)

    if job.status in {RunningJobStatus.PENDING, RunningJobStatus.RUNNING}:
        if st.button("Cancel job", key=f"cancel_job_{job.id}"):
            repository.cancel(job.id)
            st.rerun()

    if job.status == RunningJobStatus.COMPLETED:
        _render_result_summary(job.result)


if hasattr(st, "fragment"):
    @st.fragment(run_every="2s")
    def _render_job_status_fragment(job_id: str | None):
        _render_job_status_body(job_id)
else:
    def _render_job_status_fragment(job_id: str | None):
        _render_job_status_body(job_id)


def render_job_status(job_id: str | None):
    """
    Render persistent job status.

    There is intentionally no manual Refresh button.
    On Streamlit versions with st.fragment, status updates automatically every 2 seconds.
    On older Streamlit versions, the job still keeps running and status updates on normal page reruns.
    """
    _render_job_status_fragment(job_id)


def render_latest_job_status(job_type: str):
    repository = ProgressRepository()
    job = repository.latest(job_type=job_type, active_only=False)
    render_job_status(job.id if job else None)
