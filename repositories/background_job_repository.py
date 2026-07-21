from __future__ import annotations

import json
from datetime import datetime

from memory.db import get_connection
from jobs.running_job import RunningJob


class BackgroundJobRepository:
    def __init__(self, connection_factory=None):
        self._connect = connection_factory or get_connection
        self._ensure_schema()

    def _ensure_schema(self):
        conn = self._connect()
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS background_jobs (
                id TEXT PRIMARY KEY,
                job_type TEXT NOT NULL,
                status TEXT NOT NULL,
                progress REAL NOT NULL DEFAULT 0,
                stage TEXT,
                message TEXT,
                error TEXT,
                result_json TEXT,
                metadata_json TEXT NOT NULL DEFAULT '{}',
                logs_json TEXT NOT NULL DEFAULT '[]',
                cancel_requested INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                started_at TEXT,
                updated_at TEXT NOT NULL,
                finished_at TEXT
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_background_jobs_status_updated "
            "ON background_jobs(status, updated_at)"
        )
        conn.commit()
        conn.close()

    @staticmethod
    def _json(value) -> str:
        return json.dumps(value, ensure_ascii=False, default=str)

    @staticmethod
    def _date(value: str | None) -> datetime | None:
        return datetime.fromisoformat(value) if value else None

    def save(self, job: RunningJob):
        conn = self._connect()
        conn.execute(
            """
            INSERT INTO background_jobs (
                id, job_type, status, progress, stage, message, error,
                result_json, metadata_json, logs_json, cancel_requested,
                created_at, started_at, updated_at, finished_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                job_type=excluded.job_type,
                status=excluded.status,
                progress=excluded.progress,
                stage=excluded.stage,
                message=excluded.message,
                error=excluded.error,
                result_json=excluded.result_json,
                metadata_json=excluded.metadata_json,
                logs_json=excluded.logs_json,
                cancel_requested=excluded.cancel_requested,
                started_at=excluded.started_at,
                updated_at=excluded.updated_at,
                finished_at=excluded.finished_at
            """,
            (
                job.id,
                job.job_type,
                job.status,
                float(job.progress or 0),
                job.stage,
                job.message,
                job.error,
                self._json(job.result) if job.result is not None else None,
                self._json(job.metadata or {}),
                self._json((job.logs or [])[-200:]),
                int(bool(job.cancel_requested)),
                job.created_at.isoformat(),
                job.started_at.isoformat() if job.started_at else None,
                job.updated_at.isoformat(),
                job.finished_at.isoformat() if job.finished_at else None,
            ),
        )
        conn.commit()
        conn.close()

    def _from_row(self, row) -> RunningJob:
        return RunningJob(
            id=row["id"],
            job_type=row["job_type"],
            status=row["status"],
            progress=float(row["progress"] or 0),
            stage=row["stage"] or "",
            message=row["message"] or "",
            error=row["error"] or "",
            result=json.loads(row["result_json"]) if row["result_json"] else None,
            created_at=self._date(row["created_at"]) or datetime.utcnow(),
            started_at=self._date(row["started_at"]),
            updated_at=self._date(row["updated_at"]) or datetime.utcnow(),
            finished_at=self._date(row["finished_at"]),
            cancel_requested=bool(row["cancel_requested"]),
            metadata=json.loads(row["metadata_json"] or "{}"),
            logs=json.loads(row["logs_json"] or "[]"),
        )

    def get(self, job_id: str) -> RunningJob | None:
        conn = self._connect()
        row = conn.execute(
            "SELECT * FROM background_jobs WHERE id = ?", (job_id,)
        ).fetchone()
        conn.close()
        return self._from_row(row) if row else None

    def list(self, limit: int = 200) -> list[RunningJob]:
        conn = self._connect()
        rows = conn.execute(
            "SELECT * FROM background_jobs ORDER BY created_at DESC LIMIT ?",
            (int(limit),),
        ).fetchall()
        conn.close()
        return [self._from_row(row) for row in rows]


background_job_repository = BackgroundJobRepository()
