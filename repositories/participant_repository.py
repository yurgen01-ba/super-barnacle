from __future__ import annotations

import json

from memory.db import get_connection


class ParticipantRepository:
    def __init__(self):
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        connection = get_connection()
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                name TEXT NOT NULL,
                source_type TEXT NOT NULL,
                source_ref TEXT NOT NULL DEFAULT '',
                role TEXT,
                metadata_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(project_id, name, source_type, source_ref)
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_participants_project ON participants(project_id, name)"
        )
        connection.commit()
        connection.close()

    def upsert(
        self,
        *,
        project_id: str,
        name: str,
        source_type: str,
        source_ref: str = "",
        role: str | None = None,
        metadata: dict | None = None,
    ) -> None:
        clean_name = " ".join(str(name or "").split()).strip(" :;,-")
        if len(clean_name) < 2 or len(clean_name) > 120:
            return
        connection = get_connection()
        connection.execute(
            """
            INSERT INTO participants(project_id, name, source_type, source_ref, role, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(project_id, name, source_type, source_ref) DO UPDATE SET
                role = COALESCE(excluded.role, role),
                metadata_json = excluded.metadata_json,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                project_id,
                clean_name,
                source_type,
                source_ref or "",
                role,
                json.dumps(metadata or {}, ensure_ascii=False),
            ),
        )
        connection.commit()
        connection.close()

    def list_grouped(self, project_id: str) -> list[dict]:
        connection = get_connection()
        rows = connection.execute(
            """
            SELECT name, source_type, source_ref, role, updated_at
            FROM participants WHERE project_id = ?
            ORDER BY name COLLATE NOCASE, updated_at DESC
            """,
            (project_id,),
        ).fetchall()
        connection.close()
        grouped: dict[str, dict] = {}
        for row in rows:
            key = row["name"].casefold()
            item = grouped.setdefault(
                key,
                {
                    "name": row["name"],
                    "role": row["role"] or "—",
                    "sources": [],
                    "updated_at": row["updated_at"],
                },
            )
            source = row["source_type"]
            if source not in item["sources"]:
                item["sources"].append(source)
            if item["role"] == "—" and row["role"]:
                item["role"] = row["role"]
        result = []
        for item in grouped.values():
            item["sources"] = ", ".join(item["sources"])
            result.append(item)
        return result


participant_repository = ParticipantRepository()
