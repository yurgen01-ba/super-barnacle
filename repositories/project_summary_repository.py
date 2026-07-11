from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from models.project_summary import ProjectSummary


class ProjectSummaryRepository:
    def __init__(self, db_path: str | Path = "data/project_summary.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _ensure_schema(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS project_summaries (
                    project_id TEXT PRIMARY KEY,
                    payload_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def save(self, summary: ProjectSummary) -> ProjectSummary:
        payload = summary.to_dict()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO project_summaries(project_id, payload_json, updated_at)
                VALUES (?, ?, ?)
                """,
                (summary.project_id, json.dumps(payload, ensure_ascii=False), payload["updated_at"]),
            )
        return summary

    def get(self, project_id: str = "default") -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT payload_json FROM project_summaries WHERE project_id = ?",
                (project_id,),
            ).fetchone()

        if not row:
            return None

        return json.loads(row[0])


project_summary_repository = ProjectSummaryRepository()
