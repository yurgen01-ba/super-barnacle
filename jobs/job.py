from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Job:
    name: str
    source: str
    id: str = field(default_factory=lambda: str(uuid4()))
    status: JobStatus = JobStatus.QUEUED
    current_stage: str = "queued"
    progress: float = 0.0
    error: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: datetime | None = None
    finished_at: datetime | None = None

    def start(self, stage: str = "running"):
        self.status = JobStatus.RUNNING
        self.current_stage = stage
        self.started_at = datetime.utcnow()

    def complete(self):
        self.status = JobStatus.COMPLETED
        self.progress = 1.0
        self.current_stage = "completed"
        self.finished_at = datetime.utcnow()

    def fail(self, error: Exception | str):
        self.status = JobStatus.FAILED
        self.error = str(error)
        self.current_stage = "failed"
        self.finished_at = datetime.utcnow()

