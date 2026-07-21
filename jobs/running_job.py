from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


class RunningJobStatus:
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class RunningJob:
    id: str
    job_type: str
    status: str = RunningJobStatus.PENDING
    progress: float = 0.0
    stage: str = ""
    message: str = ""
    error: str = ""
    result: Any = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: datetime | None = None
    updated_at: datetime = field(default_factory=datetime.utcnow)
    finished_at: datetime | None = None
    cancel_requested: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
    logs: list[str] = field(default_factory=list)

    @classmethod
    def create(cls, job_type: str, metadata: dict[str, Any] | None = None) -> "RunningJob":
        return cls(
            id=str(uuid4()),
            job_type=job_type,
            metadata=metadata or {},
        )

    def mark_running(self):
        self.status = RunningJobStatus.RUNNING
        self.started_at = self.started_at or datetime.utcnow()
        self.touch()

    def mark_completed(self, result: Any = None):
        self.status = RunningJobStatus.COMPLETED
        self.progress = 1.0
        self.result = result
        self.finished_at = datetime.utcnow()
        self.touch()

    def mark_failed(self, error: Exception | str):
        self.status = RunningJobStatus.FAILED
        self.error = str(error)
        self.finished_at = datetime.utcnow()
        self.touch()

    def mark_cancelled(self):
        self.status = RunningJobStatus.CANCELLED
        self.finished_at = datetime.utcnow()
        self.touch()

    def request_cancel(self):
        self.cancel_requested = True
        self.touch()

    def update_progress(self, progress: float | None = None, stage: str | None = None, message: str | None = None):
        if progress is not None:
            self.progress = max(0.0, min(1.0, float(progress)))
        if stage is not None:
            self.stage = stage
        if message is not None:
            self.message = message
            self.add_log(message)
        self.touch()

    def add_log(self, message: str):
        timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
        self.logs.append(f"[{timestamp}] {message}")

    def touch(self):
        self.updated_at = datetime.utcnow()

    def is_active(self) -> bool:
        return self.status in {RunningJobStatus.PENDING, RunningJobStatus.RUNNING}

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "job_type": self.job_type,
            "status": self.status,
            "progress": self.progress,
            "stage": self.stage,
            "message": self.message,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "updated_at": self.updated_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "cancel_requested": self.cancel_requested,
            "metadata": self.metadata,
            "logs": self.logs[-100:],
        }
