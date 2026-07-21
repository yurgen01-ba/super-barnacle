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
    "slack_messages_per_chunk": 12,
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
    def __init__(self, connection_factory=None):
        self._connect = connection_factory or get_connection
        if connection_factory is None:
            init_db()
        self._ensure_schema()

    def _ensure_schema(self):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                owner_user_id TEXT,
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
        cur.execute("""
            CREATE TABLE IF NOT EXISTS project_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                user_id TEXT,
                email TEXT NOT NULL,
                name TEXT,
                role TEXT NOT NULL DEFAULT 'member',
                status TEXT NOT NULL DEFAULT 'active',
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(project_id, email)
            )
        """)
        project_columns = {
            row[1] for row in cur.execute("PRAGMA table_info(projects)").fetchall()
        }
        if "owner_user_id" not in project_columns:
            cur.execute("ALTER TABLE projects ADD COLUMN owner_user_id TEXT")
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
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_projects_owner ON projects(owner_user_id, created_at)"
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_project_members_user ON project_members(user_id, status)"
        )
        cur.execute(
            """
            INSERT OR IGNORE INTO project_members(project_id, user_id, email, name, role, status)
            SELECT id, owner_user_id, 'owner:' || owner_user_id, name, 'owner', 'active'
            FROM projects WHERE owner_user_id IS NOT NULL
            """
        )
        conn.commit()
        conn.close()

    def ensure_user_workspace(self, user_id: str, email: str = "", name: str = "") -> dict:
        """Claim legacy projects once, then guarantee a private workspace."""
        if not user_id:
            raise ValueError("User id is required")
        conn = self._connect()
        with conn:
            normalized_email = str(email or "").strip().lower()
            if normalized_email:
                conn.execute(
                    """
                    UPDATE project_members SET user_id = ?, name = COALESCE(NULLIF(?, ''), name),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE lower(email) = ? AND user_id IS NULL
                    """,
                    (user_id, name, normalized_email),
                )
                conn.execute(
                    """
                    UPDATE project_members SET email = ?, name = COALESCE(NULLIF(?, ''), name),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND role = 'owner' AND email LIKE 'owner:%'
                    """,
                    (normalized_email, name, user_id),
                )
            accessible = conn.execute(
                """
                SELECT COUNT(DISTINCT p.id) FROM projects p
                LEFT JOIN project_members m ON m.project_id = p.id
                WHERE p.owner_user_id = ? OR (m.user_id = ? AND m.status = 'active')
                """,
                (user_id, user_id),
            ).fetchone()[0]
            if not accessible:
                legacy = conn.execute(
                    "SELECT COUNT(*) FROM projects WHERE owner_user_id IS NULL"
                ).fetchone()[0]
                if legacy:
                    conn.execute(
                        "UPDATE projects SET owner_user_id = ? WHERE owner_user_id IS NULL",
                        (user_id,),
                    )
                    owner_email = normalized_email or f"owner:{user_id}"
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO project_members(project_id, user_id, email, name, role, status)
                        SELECT id, ?, ?, ?, 'owner', 'active' FROM projects WHERE owner_user_id = ?
                        """,
                        (user_id, owner_email, name, user_id),
                    )
                else:
                    project_id = str(uuid4())
                    conn.execute(
                        "INSERT INTO projects (id, name, owner_user_id) VALUES (?, ?, ?)",
                        (project_id, DEFAULT_PROJECT_NAME, user_id),
                    )
                    conn.execute(
                        """
                        INSERT INTO project_members(project_id, user_id, email, name, role, status)
                        VALUES (?, ?, ?, ?, 'owner', 'active')
                        """,
                        (project_id, user_id, normalized_email or f"owner:{user_id}", name),
                    )
        conn.close()
        return self.list_projects(user_id)[0]

    def list_projects(self, user_id: str) -> list[dict]:
        if not user_id:
            return []
        conn = self._connect()
        rows = conn.execute(
            """
            SELECT DISTINCT p.* FROM projects p
            LEFT JOIN project_members m ON m.project_id = p.id
            WHERE p.owner_user_id = ? OR (m.user_id = ? AND m.status = 'active')
            ORDER BY p.created_at ASC, p.name ASC
            """,
            (user_id, user_id),
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_project(self, project_id: str, user_id: str) -> dict | None:
        if not user_id:
            return None
        conn = self._connect()
        row = conn.execute(
            """
            SELECT DISTINCT p.* FROM projects p
            LEFT JOIN project_members m ON m.project_id = p.id
            WHERE p.id = ? AND (p.owner_user_id = ? OR (m.user_id = ? AND m.status = 'active'))
            """,
            (project_id, user_id, user_id),
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    def create_project(self, name: str, user_id: str, email: str = "", owner_name: str = "") -> dict:
        clean_name = re.sub(r"\s+", " ", str(name or "").strip())
        if not clean_name:
            raise ValueError("Project name is required")
        project_id = str(uuid4())
        if not user_id:
            raise ValueError("User id is required")
        conn = self._connect()
        conn.execute(
            "INSERT INTO projects (id, name, owner_user_id) VALUES (?, ?, ?)",
            (project_id, clean_name[:120], user_id),
        )
        conn.execute(
            """
            INSERT INTO project_members(project_id, user_id, email, name, role, status)
            VALUES (?, ?, ?, ?, 'owner', 'active')
            """,
            (project_id, user_id, str(email or "").strip().lower() or f"owner:{user_id}", owner_name),
        )
        conn.commit()
        conn.close()
        self.log_event(project_id, "project", "Проект создан", {"name": clean_name})
        return self.get_project(project_id, user_id)

    def rename_project(self, project_id: str, name: str, user_id: str):
        clean_name = re.sub(r"\s+", " ", str(name or "").strip())
        if not clean_name:
            raise ValueError("Project name is required")
        conn = self._connect()
        cursor = conn.execute(
            "UPDATE projects SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND owner_user_id = ?",
            (clean_name[:120], project_id, user_id),
        )
        if not cursor.rowcount:
            conn.close()
            raise PermissionError("Project is not available to this user")
        conn.commit()
        conn.close()
        self.log_event(project_id, "project", "Проект переименован", {"name": clean_name})

    def delete_project(self, project_id: str, user_id: str):
        projects = self.list_projects(user_id)
        if len(projects) <= 1:
            raise ValueError("The only project cannot be deleted")
        if not self.get_project(project_id, user_id):
            raise PermissionError("Project is not available to this user")
        conn = self._connect()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM chunks WHERE document_id IN (SELECT id FROM documents WHERE project_id = ?)",
            (project_id,),
        )
        project_tables = [
            row[0]
            for row in cur.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
            ).fetchall()
        ]
        for table in project_tables:
            if table == "projects" or not re.fullmatch(r"[A-Za-z0-9_]+", table):
                continue
            columns = {
                row[1] for row in cur.execute(f"PRAGMA table_info({table})").fetchall()
            }
            if "project_id" in columns:
                cur.execute(f"DELETE FROM {table} WHERE project_id = ?", (project_id,))
        cur.execute(
            "DELETE FROM projects WHERE id = ? AND owner_user_id = ?",
            (project_id, user_id),
        )
        conn.commit()
        conn.close()
        artifact_repository.delete_by_project(project_id)
        extraction_repository.delete_by_project(project_id)

    def is_owner(self, project_id: str, user_id: str) -> bool:
        conn = self._connect()
        row = conn.execute(
            "SELECT 1 FROM projects WHERE id = ? AND owner_user_id = ?",
            (project_id, user_id),
        ).fetchone()
        conn.close()
        return bool(row)

    def list_members(self, project_id: str, requesting_user_id: str) -> list[dict]:
        if not self.get_project(project_id, requesting_user_id):
            raise PermissionError("Project is not available to this user")
        conn = self._connect()
        rows = conn.execute(
            """
            SELECT id, user_id, email, name, role, status, added_at, updated_at
            FROM project_members WHERE project_id = ?
            ORDER BY CASE role WHEN 'owner' THEN 0 ELSE 1 END, lower(email)
            """,
            (project_id,),
        ).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_member(
        self,
        project_id: str,
        requesting_user_id: str,
        *,
        email: str,
        user_id: str | None = None,
        name: str = "",
    ) -> dict:
        if not self.is_owner(project_id, requesting_user_id):
            raise PermissionError("Only the project owner can manage access")
        normalized_email = str(email or "").strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalized_email):
            raise ValueError("A valid email is required")
        conn = self._connect()
        with conn:
            conn.execute(
                """
                INSERT INTO project_members(project_id, user_id, email, name, role, status)
                VALUES (?, ?, ?, ?, 'member', 'active')
                ON CONFLICT(project_id, email) DO UPDATE SET
                    user_id = COALESCE(excluded.user_id, project_members.user_id),
                    name = COALESCE(NULLIF(excluded.name, ''), project_members.name),
                    status = 'active', updated_at = CURRENT_TIMESTAMP
                """,
                (project_id, user_id, normalized_email, name),
            )
        row = conn.execute(
            "SELECT * FROM project_members WHERE project_id = ? AND email = ?",
            (project_id, normalized_email),
        ).fetchone()
        conn.close()
        return dict(row)

    def set_member_status(
        self, project_id: str, requesting_user_id: str, member_id: int, status: str
    ) -> None:
        if not self.is_owner(project_id, requesting_user_id):
            raise PermissionError("Only the project owner can manage access")
        if status not in {"active", "blocked"}:
            raise ValueError("Invalid member status")
        conn = self._connect()
        cursor = conn.execute(
            """
            UPDATE project_members SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND project_id = ? AND role != 'owner'
            """,
            (status, member_id, project_id),
        )
        conn.commit()
        conn.close()
        if not cursor.rowcount:
            raise ValueError("Project member not found")

    def remove_member(self, project_id: str, requesting_user_id: str, member_id: int) -> None:
        if not self.is_owner(project_id, requesting_user_id):
            raise PermissionError("Only the project owner can manage access")
        conn = self._connect()
        cursor = conn.execute(
            "DELETE FROM project_members WHERE id = ? AND project_id = ? AND role != 'owner'",
            (member_id, project_id),
        )
        conn.commit()
        conn.close()
        if not cursor.rowcount:
            raise ValueError("Project member not found")

    def get_settings(self, project_id: str) -> dict:
        conn = self._connect()
        row = conn.execute(
            "SELECT settings_json FROM project_settings WHERE project_id = ?",
            (project_id,),
        ).fetchone()
        conn.close()
        stored = json.loads(row["settings_json"] or "{}") if row else {}
        return {**DEFAULT_MEETING_SETTINGS, **stored}

    def save_settings(self, project_id: str, settings: dict):
        payload = {**DEFAULT_MEETING_SETTINGS, **(settings or {})}
        conn = self._connect()
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
        conn = self._connect()
        conn.execute(
            "INSERT INTO project_events(project_id, event_type, title, details_json) VALUES (?, ?, ?, ?)",
            (project_id, event_type, title, json.dumps(details or {}, ensure_ascii=False, default=str)),
        )
        conn.commit()
        conn.close()

    def list_events(self, project_id: str, limit: int = 20) -> list[dict]:
        conn = self._connect()
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
        conn = self._connect()
        source_count = conn.execute(
            "SELECT COUNT(*) FROM documents WHERE project_id = ?", (project_id,)
        ).fetchone()[0]
        knowledge_count = conn.execute(
            "SELECT COUNT(*) FROM knowledge WHERE project_id = ?", (project_id,)
        ).fetchone()[0]
        conn.close()
        all_artifact_count = artifact_repository.count_by_project(project_id)
        user_artifact_count = artifact_repository.count_user_generated_by_project(project_id)
        # A transparent readiness score: sources establish coverage, extracted
        # knowledge and artifacts establish usable depth.
        readiness = min(
            100,
            (min(source_count, 5) * 10)
            + (min(knowledge_count, 50) * 1)
            + (min(all_artifact_count, 10) * 2),
        )
        return {
            "knowledge_health": readiness,
            "sources": source_count,
            "knowledge_items": knowledge_count,
            "artifacts": user_artifact_count,
        }


workspace_repository = WorkspaceRepository()
