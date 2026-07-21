from __future__ import annotations

import threading

from jobs.running_job import RunningJob
from repositories.background_job_repository import background_job_repository


class RunningJobStore:
    """
    Process-local job registry.

    This intentionally keeps jobs outside Streamlit render/session lifecycle.
    Jobs survive tab switches and Streamlit reruns while the Python process is alive.
    """

    def __init__(self, persistent_repository=None):
        self._lock = threading.RLock()
        self._persistent_repository = persistent_repository or background_job_repository
        self._jobs: dict[str, RunningJob] = {
            job.id: job for job in self._persistent_repository.list()
        }

    def add(self, job: RunningJob) -> RunningJob:
        with self._lock:
            self._jobs[job.id] = job
            self._persistent_repository.save(job)
        return job

    def get(self, job_id: str) -> RunningJob | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                return job
            job = self._persistent_repository.get(job_id)
            if job:
                self._jobs[job.id] = job
            return job

    def list(self, job_type: str | None = None, active_only: bool = False) -> list[RunningJob]:
        with self._lock:
            jobs = list(self._jobs.values())

        if job_type:
            jobs = [job for job in jobs if job.job_type == job_type]

        if active_only:
            jobs = [job for job in jobs if job.is_active()]

        return sorted(jobs, key=lambda job: job.created_at, reverse=True)

    def find_latest(self, job_type: str | None = None, active_only: bool = False) -> RunningJob | None:
        jobs = self.list(job_type=job_type, active_only=active_only)
        return jobs[0] if jobs else None

    def update(self, job: RunningJob):
        with self._lock:
            self._jobs[job.id] = job
            self._persistent_repository.save(job)

    def cancel(self, job_id: str) -> bool:
        job = self.get(job_id)
        if not job:
            return False
        job.request_cancel()
        self.update(job)
        return True


running_job_store = RunningJobStore()
