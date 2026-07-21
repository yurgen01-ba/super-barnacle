from __future__ import annotations

import hashlib
import json
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from config import DB_PATH
from repositories.atlassian_connection_repository import TokenCipher


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SlackConnectionRepository:
    def __init__(
        self, db_path: str | None = None, cipher: TokenCipher | None = None
    ) -> None:
        self.db_path = db_path or DB_PATH
        self.cipher = cipher or TokenCipher()
        self._init_schema()

    @contextmanager
    def _connect(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS slack_oauth_states (
                    state_hash TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS slack_connections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    team_id TEXT NOT NULL,
                    team_name TEXT NOT NULL,
                    authed_user_id TEXT NOT NULL DEFAULT '',
                    scopes_json TEXT NOT NULL DEFAULT '[]',
                    access_token_encrypted TEXT NOT NULL,
                    refresh_token_encrypted TEXT,
                    expires_at TEXT,
                    status TEXT NOT NULL DEFAULT 'connected',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(user_id, project_id, team_id)
                );
                CREATE INDEX IF NOT EXISTS idx_slack_connections_project
                ON slack_connections(project_id, user_id);
                """
            )

    def create_state(self, user_id: str, project_id: str, ttl_minutes: int = 15) -> str:
        state = secrets.token_urlsafe(40)
        state_hash = hashlib.sha256(state.encode("utf-8")).hexdigest()
        now = _utcnow()
        with self._connect() as conn:
            conn.execute("DELETE FROM slack_oauth_states WHERE expires_at < ?", (now.isoformat(),))
            conn.execute(
                "INSERT INTO slack_oauth_states VALUES (?, ?, ?, ?, ?)",
                (
                    state_hash, user_id, project_id,
                    (now + timedelta(minutes=ttl_minutes)).isoformat(), now.isoformat(),
                ),
            )
        return state

    def consume_state(self, state: str) -> dict | None:
        state_hash = hashlib.sha256(str(state or "").encode("utf-8")).hexdigest()
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM slack_oauth_states WHERE state_hash=?", (state_hash,)
            ).fetchone()
            conn.execute("DELETE FROM slack_oauth_states WHERE state_hash=?", (state_hash,))
        if not row or datetime.fromisoformat(row["expires_at"]) < _utcnow():
            return None
        return dict(row)

    def save(
        self, *, user_id: str, project_id: str, team_id: str, team_name: str,
        authed_user_id: str, scopes: list[str], access_token: str,
        refresh_token: str | None = None, expires_in: int | None = None,
    ) -> dict:
        now = _utcnow()
        expires_at = (
            (now + timedelta(seconds=int(expires_in))).isoformat() if expires_in else None
        )
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO slack_connections(
                    user_id, project_id, team_id, team_name, authed_user_id,
                    scopes_json, access_token_encrypted, refresh_token_encrypted,
                    expires_at, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'connected', ?, ?)
                ON CONFLICT(user_id, project_id, team_id) DO UPDATE SET
                    team_name=excluded.team_name,
                    authed_user_id=excluded.authed_user_id,
                    scopes_json=excluded.scopes_json,
                    access_token_encrypted=excluded.access_token_encrypted,
                    refresh_token_encrypted=excluded.refresh_token_encrypted,
                    expires_at=excluded.expires_at,
                    status='connected', updated_at=excluded.updated_at
                """,
                (
                    user_id, project_id, team_id, team_name, authed_user_id,
                    json.dumps(scopes), self.cipher.encrypt(access_token),
                    self.cipher.encrypt(refresh_token), expires_at,
                    now.isoformat(), now.isoformat(),
                ),
            )
        connections = self.list_for_project(project_id, user_id)
        return next(item for item in connections if item["team_id"] == team_id)

    def list_for_project(self, project_id: str, user_id: str) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT id, user_id, project_id, team_id, team_name,
                          authed_user_id, scopes_json, expires_at, status,
                          created_at, updated_at
                   FROM slack_connections
                   WHERE project_id=? AND user_id=? ORDER BY team_name""",
                (project_id, user_id),
            ).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["scopes"] = json.loads(item.pop("scopes_json", "[]") or "[]")
            result.append(item)
        return result

    def get_with_token(self, connection_id: int, user_id: str, project_id: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM slack_connections WHERE id=? AND user_id=? AND project_id=?",
                (connection_id, user_id, project_id),
            ).fetchone()
        if not row:
            return None
        item = dict(row)
        item["access_token"] = self.cipher.decrypt(item.pop("access_token_encrypted", ""))
        item["refresh_token"] = self.cipher.decrypt(item.pop("refresh_token_encrypted", ""))
        item["scopes"] = json.loads(item.pop("scopes_json", "[]") or "[]")
        return item

    def delete(self, connection_id: int, user_id: str, project_id: str) -> bool:
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM slack_connections WHERE id=? AND user_id=? AND project_id=?",
                (connection_id, user_id, project_id),
            )
        return cursor.rowcount > 0


slack_connection_repository = SlackConnectionRepository()
