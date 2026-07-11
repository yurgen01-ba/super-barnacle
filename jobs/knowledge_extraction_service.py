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
        return background_job_executor.submit(
            KNOWLEDGE_EXTRACTION_JOB,
            extraction_callable,
            *args,
            metadata=metadata,
            **kwargs,
        )

    def latest(self, active_only: bool = False) -> RunningJob | None:
        return running_job_store.find_latest(
            job_type=KNOWLEDGE_EXTRACTION_JOB,
            active_only=active_only,
        )

    def get(self, job_id: str) -> RunningJob | None:
        return running_job_store.get(job_id)

    def cancel(self, job_id: str) -> bool:
        return running_job_store.cancel(job_id)
