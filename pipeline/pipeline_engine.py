from typing import Any

from core.logger import get_logger
from jobs.job import Job
from pipeline.base_pipeline import BasePipeline


logger = get_logger(__name__)


class PipelineEngine:
    def run(self, pipeline: BasePipeline, job: Job | None = None, *args, **kwargs) -> Any:
        if job:
            job.start(stage="pipeline_started")

        try:
            logger.info("Pipeline started: %s", pipeline.__class__.__name__)
            result = pipeline.run(*args, **kwargs)

            if job:
                job.complete()

            logger.info("Pipeline completed: %s", pipeline.__class__.__name__)
            return result

        except Exception as exc:
            if job:
                job.fail(exc)

            logger.exception("Pipeline failed: %s", pipeline.__class__.__name__)
            raise

