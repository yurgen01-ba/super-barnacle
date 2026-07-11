from abc import ABC, abstractmethod
from typing import Any

from jobs.job import Job
from progress.progress_manager import ProgressManager


class BasePipeline(ABC):
    def __init__(self, job: Job | None = None, progress: ProgressManager | None = None):
        self.job = job
        self.progress = progress

    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        raise NotImplementedError

