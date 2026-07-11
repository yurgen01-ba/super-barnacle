from __future__ import annotations

from jobs.running_job import RunningJob


class JobProgress:
    """
    Convenience progress callback passed into extraction services.
    """

    def __init__(self, job: RunningJob):
        self.job = job

    def update(self, progress: float | None = None, stage: str | None = None, message: str | None = None):
        self.job.update_progress(progress=progress, stage=stage, message=message)

    def check_cancelled(self):
        if self.job.cancel_requested:
            raise RuntimeError("Job cancellation requested")
