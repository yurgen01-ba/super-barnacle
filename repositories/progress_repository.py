from __future__ import annotations

from jobs.running_job import RunningJob
from jobs.running_job_store import running_job_store


class ProgressRepository:
    """
    Read/write API for job progress.

    UI should read progress from here instead of storing progress in Streamlit session_state.
    """

    def get(self, job_id: str) -> RunningJob | None:
        return running_job_store.get(job_id)

    def latest(self, job_type: str | None = None, active_only: bool = False) -> RunningJob | None:
        return running_job_store.find_latest(job_type=job_type, active_only=active_only)

    def list(self, job_type: str | None = None, active_only: bool = False) -> list[RunningJob]:
        return running_job_store.list(job_type=job_type, active_only=active_only)

    def update(
        self,
        job_id: str,
        progress: float | None = None,
        stage: str | None = None,
        message: str | None = None,
    ) -> RunningJob | None:
        job = running_job_store.get(job_id)
        if not job:
            return None

        job.update_progress(progress=progress, stage=stage, message=message)
        running_job_store.update(job)
        return job

    def cancel(self, job_id: str) -> bool:
        return running_job_store.cancel(job_id)
