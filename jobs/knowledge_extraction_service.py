from __future__ import annotations

from typing import Callable, Any

from jobs.background_job_executor import background_job_executor
from jobs.running_job import RunningJob
from jobs.running_job_store import running_job_store


KNOWLEDGE_EXTRACTION_JOB = "knowledge_extraction"


class KnowledgeExtractionJobService:
    """
    Starts or attaches to knowledge extraction jobs.

    The extraction callable receives `job=RunningJob` directly from BackgroundJobExecutor.
    """

    def start(
        self,
        extraction_callable: Callable[..., Any],
        *args,
        metadata: dict[str, Any] | None = None,
        **kwargs,
    ) -> RunningJob:
        job_metadata = dict(metadata or {})
        try:
            from ui_v2.auth import get_authenticated_email

            notification_email = get_authenticated_email()
            if notification_email:
                job_metadata.setdefault("notification_email", notification_email)
        except Exception:
            pass
        return background_job_executor.submit(
            KNOWLEDGE_EXTRACTION_JOB,
            extraction_callable,
            *args,
            metadata=job_metadata,
            **kwargs,
        )

    def latest(
        self,
        active_only: bool = False,
        project_id: str | None = None,
    ) -> RunningJob | None:
        jobs = running_job_store.list(
            job_type=KNOWLEDGE_EXTRACTION_JOB,
            active_only=active_only,
        )
        if project_id is not None:
            jobs = [
                job for job in jobs
                if (job.metadata or {}).get("project_id", "default") == project_id
            ]
        return jobs[0] if jobs else None

    def get(self, job_id: str) -> RunningJob | None:
        return running_job_store.get(job_id)

    def cancel(self, job_id: str) -> bool:
        return running_job_store.cancel(job_id)
