from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from typing import Callable, Any

from jobs.running_job import RunningJob
from jobs.running_job_store import running_job_store
from services.email_notification_service import email_notification_service


class BackgroundJobExecutor:
    """
    Runs jobs in background threads.

    UI starts a job and immediately returns.
    Streamlit reruns/tab switches do not stop the job.
    """

    def __init__(self, max_workers: int = 3):
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._futures: dict[str, Future] = {}

    def submit(
        self,
        job_type: str,
        fn: Callable[..., Any],
        *args,
        metadata: dict[str, Any] | None = None,
        **kwargs,
    ) -> RunningJob:
        job = RunningJob.create(job_type=job_type, metadata=metadata)
        running_job_store.add(job)

        future = self._executor.submit(self._run_job, job, fn, *args, **kwargs)
        self._futures[job.id] = future

        return job

    def _run_job(self, job: RunningJob, fn: Callable[..., Any], *args, **kwargs):
        job.mark_running()
        running_job_store.update(job)

        try:
            kwargs["job"] = job
            result = fn(*args, **kwargs)

            if job.cancel_requested:
                job.mark_cancelled()
            else:
                job.mark_completed(result=result)

        except Exception as exc:
            job.mark_failed(exc)

        try:
            if email_notification_service.notify_job_finished(job):
                job.logs.append("Email notification sent.")
            elif (job.metadata or {}).get("notification_email"):
                job.logs.append("Email notification skipped: SMTP is not configured.")
        except Exception as exc:
            job.logs.append(f"Email notification failed: {exc}")

        running_job_store.update(job)

    def get_future(self, job_id: str) -> Future | None:
        return self._futures.get(job_id)


background_job_executor = BackgroundJobExecutor()
