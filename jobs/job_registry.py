from __future__ import annotations

from jobs.running_job import RunningJob
from jobs.running_job_store import running_job_store


class JobRegistry:
    """
    Query API for all background jobs.

    Supports future multiple extraction jobs without changing UI callers.
    """

    def list_all(self) -> list[RunningJob]:
        return running_job_store.list()

    def list_active(self) -> list[RunningJob]:
        return running_job_store.list(active_only=True)

    def list_by_type(self, job_type: str, active_only: bool = False) -> list[RunningJob]:
        return running_job_store.list(job_type=job_type, active_only=active_only)

    def latest_by_type(self, job_type: str, active_only: bool = False) -> RunningJob | None:
        return running_job_store.find_latest(job_type=job_type, active_only=active_only)

    def cancel(self, job_id: str) -> bool:
        return running_job_store.cancel(job_id)
