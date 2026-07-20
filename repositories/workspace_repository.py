from __future__ import annotations

import json
import re
from datetime import datetime
from uuid import uuid4

from memory.db import get_connection, init_db
from repositories.artifact_repository import artifact_repository
from repositories.extraction_repository import extraction_repository


DEFAULT_PROJECT_ID = "default"
DEFAULT_PROJECT_NAME = "OrgMeter"

DEFAULT_MEETING_SETTINGS = {
    "language": "ru",
    "extract_canonical_facts": True,
    "fact_extractor_model": "qwen2.5:7b",
    "fact_extractor_host": "http://localhost:11434",
    "fact_extractor_timeout_seconds": 240,
    "transcript_extractor_provider": "ollama",
    "transcript_extractor_model": "qwen2.5:7b",
    "transcript_extractor_host": "http://localhost:11434",
    "transcript_extractor_timeout_seconds": 180,
    "manual_audio_segments": False,
    "manual_segment_minutes": 20,
    "analyze_screen": False,
    "screen_interval_seconds": 60,
    "screen_dedup_distance": 8,
    "vision_model": "qwen2.5vl:7b",
    "vision_host": "http://localhost:11434",
    "vision_timeout_seconds": 180,
}


class WorkspaceRepository:
    def __init__(self):
        init_db()
        self._ensure_schema()

    def _ensure_schema(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS project_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                title TEXT NOT NULL,
                details_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS project_settings (
                project_id TEXT PRIMARY KEY,
                settings_json TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        project_count = cur.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
        if not project_count:
            cur.execute(
                "INSERT INTO projects (id, name) VALUES (?, ?)",
                (DEFAULT_PROJECT_ID, DEFAULT_PROJECT_NAME),
            )
        for table in ("knowledge", "timeline", "documents"):
            columns = {
                row[1] for row in cur.execute(f"PRAGMA table_info({table})").fetchall()
            }
            if columns and "project_id" not in columns:
                cur.execute(
                    f"ALTER TABLE {table} ADD COLUMN project_id TEXT NOT NULL DEFAULT 'default'"
                )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_project_events_project ON project_events(project_id, created_at)"
        )
        conn.commit()
        conn.close()

    def list_projects(self) -> list[dict]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM projects ORDER BY created_at ASC, name ASC"
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_project(self, project_id: str) -> dict | None:
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM projects WHERE id = ?", (project_id,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    def create_project(self, name: str) -> dict:
        clean_name = re.sub(r"\s+", " ", str(name or "").strip())
        if not clean_name:
            raise ValueError("Project name is required")
        project_id = str(uuid4())
        conn = get_connection()
        conn.execute(
            "INSERT INTO projects (id, name) VALUES (?, ?)",
            (project_id, clean_name[:120]),
        )
        conn.commit()
        conn.close()
        self.log_event(project_id, "project", "Проект создан", {"name": clean_name})
        return self.get_project(project_id)

    def rename_project(self, project_id: str, name: str):
        clean_name = re.sub(r"\s+", " ", str(name or "").strip())
        if not clean_name:
            raise ValueError("Project name is required")
        conn = get_connection()
        conn.execute(
            "UPDATE projects SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (clean_name[:120], project_id),
        )
        conn.commit()
        conn.close()
        self.log_event(project_id, "project", "Проект переименован", {"name": clean_name})

    def delete_project(self, project_id: str):
        projects = self.list_projects()
        if len(projects) <= 1:
            raise ValueError("The only project cannot be deleted")
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM chunks WHERE document_id IN (SELECT id FROM documents WHERE project_id = ?)",
            (project_id,),
        )
        for table in ("knowledge", "timeline", "documents"):
            cur.execute(f"DELETE FROM {table} WHERE project_id = ?", (project_id,))
        fact_columns = {
            row[1] for row in cur.execute("PRAGMA table_info(facts)").fetchall()
        }
        if "project_id" in fact_columns:
            cur.execute("DELETE FROM facts WHERE project_id = ?", (project_id,))
        cur.execute("DELETE FROM project_events WHERE project_id = ?", (project_id,))
        cur.execute("DELETE FROM project_settings WHERE project_id = ?", (project_id,))
        cur.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        conn.commit()
        conn.close()
        artifact_repository.delete_by_project(project_id)
        extraction_repository.delete_by_project(project_id)

    def get_settings(self, project_id: str) -> dict:
        conn = get_connection()
        row = conn.execute(
            "SELECT settings_json FROM project_settings WHERE project_id = ?",
            (project_id,),
        ).fetchone()
        conn.close()
        stored = json.loads(row["settings_json"] or "{}") if row else {}
        return {**DEFAULT_MEETING_SETTINGS, **stored}

    def save_settings(self, project_id: str, settings: dict):
        payload = {**DEFAULT_MEETING_SETTINGS, **(settings or {})}
        conn = get_connection()
        conn.execute(
            """
            INSERT INTO project_settings(project_id, settings_json, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(project_id) DO UPDATE SET
                settings_json = excluded.settings_json,
                updated_at = CURRENT_TIMESTAMP
            """,
            (project_id, json.dumps(payload, ensure_ascii=False)),
        )
        conn.commit()
        conn.close()
        self.log_event(project_id, "settings", "Настройки проекта обновлены", payload)

    def log_event(
        self,
        project_id: str,
        event_type: str,
        title: str,
        details: dict | None = None,
    ):
        conn = get_connection()
        conn.execute(
            "INSERT INTO project_events(project_id, event_type, title, details_json) VALUES (?, ?, ?, ?)",
            (project_id, event_type, title, json.dumps(details or {}, ensure_ascii=False, default=str)),
        )
        conn.commit()
        conn.close()

    def list_events(self, project_id: str, limit: int = 20) -> list[dict]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM project_events WHERE project_id = ? ORDER BY created_at DESC, id DESC LIMIT ?",
            (project_id, limit),
        ).fetchall()
        conn.close()
        result = []
        for row in rows:
            item = dict(row)
            item["details"] = json.loads(item.pop("details_json") or "{}")
            result.append(item)
        return result

    def dashboard_metrics(self, project_id: str) -> dict:
        conn = get_connection()
        source_count = conn.execute(
            "SELECT COUNT(*) FROM documents WHERE project_id = ?", (project_id,)
        ).fetchone()[0]
        knowledge_count = conn.execute(
            "SELECT COUNT(*) FROM knowledge WHERE project_id = ?", (project_id,)
        ).fetchone()[0]
        conn.close()
        artifact_count = artifact_repository.count_by_project(project_id)
        # A transparent readiness score: sources establish coverage, extracted
        # knowledge and artifacts establish usable depth.
        readiness = min(
            100,
            (min(source_count, 5) * 10)
            + (min(knowledge_count, 50) * 1)
            + (min(artifact_count, 10) * 2),
        )
        return {
            "knowledge_health": readiness,
            "sources": source_count,
            "knowledge_items": knowledge_count,
            "artifacts": artifact_count,
        }


workspace_repository = WorkspaceRepository()
