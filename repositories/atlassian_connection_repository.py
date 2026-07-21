from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography.fernet import Fernet

from config import DB_PATH


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TokenCipher:
    """Encrypt OAuth tokens at rest with a deployment-specific Fernet key."""

    def __init__(self, key: str | bytes | None = None, key_path: str | None = None):
        if key:
            raw = key.encode("utf-8") if isinstance(key, str) else key
        else:
            configured = os.getenv("PROJECT_BRAIN_TOKEN_ENCRYPTION_KEY", "").strip()
            if configured:
                raw = configured.encode("utf-8")
            else:
                path = Path(key_path or os.getenv(
                    "PROJECT_BRAIN_TOKEN_KEY_PATH", "data/.oauth_token_key"
                ))
                path.parent.mkdir(parents=True, exist_ok=True)
                if path.exists():
                    raw = path.read_bytes().strip()
                else:
                    raw = Fernet.generate_key()
                    path.write_bytes(raw)
                    try:
                        os.chmod(path, 0o600)
                    except OSError:
                        pass
        try:
            self._fernet = Fernet(raw)
        except (TypeError, ValueError):
            derived = hashlib.sha256(raw).digest()
            self._fernet = Fernet(base64.urlsafe_b64encode(derived))

    def encrypt(self, value: str | None) -> str:
        if not value:
            return ""
        return self._fernet.encrypt(value.encode("utf-8")).decode("ascii")

    def decrypt(self, value: str | None) -> str:
        if not value:
            return ""
        return self._fernet.decrypt(value.encode("ascii")).decode("utf-8")


class AtlassianConnectionRepository:
    def __init__(self, db_path: str | None = None, cipher: TokenCipher | None = None):
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
                CREATE TABLE IF NOT EXISTS atlassian_oauth_states (
                    state_hash TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS atlassian_connections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    cloud_id TEXT NOT NULL,
                    site_name TEXT NOT NULL,
                    site_url TEXT NOT NULL,
                    scopes_json TEXT NOT NULL DEFAULT '[]',
                    access_token_encrypted TEXT NOT NULL,
                    refresh_token_encrypted TEXT,
                    expires_at TEXT,
                    status TEXT NOT NULL DEFAULT 'connected',
                    last_sync_at TEXT,
                    last_sync_details_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(user_id, project_id, cloud_id)
                );
                CREATE INDEX IF NOT EXISTS idx_atlassian_connections_project
                ON atlassian_connections(project_id, user_id);
                """
            )

    def create_state(self, user_id: str, project_id: str, ttl_minutes: int = 15) -> str:
        state = secrets.token_urlsafe(40)
        state_hash = hashlib.sha256(state.encode("utf-8")).hexdigest()
        now = _utcnow()
        with self._connect() as conn:
            conn.execute("DELETE FROM atlassian_oauth_states WHERE expires_at < ?", (now.isoformat(),))
            conn.execute(
                "INSERT INTO atlassian_oauth_states VALUES (?, ?, ?, ?, ?)",
                (state_hash, user_id, project_id, (now + timedelta(minutes=ttl_minutes)).isoformat(), now.isoformat()),
            )
        return state

    def consume_state(self, state: str) -> dict | None:
        state_hash = hashlib.sha256(str(state or "").encode("utf-8")).hexdigest()
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM atlassian_oauth_states WHERE state_hash = ?", (state_hash,)
            ).fetchone()
            conn.execute("DELETE FROM atlassian_oauth_states WHERE state_hash = ?", (state_hash,))
        if not row or datetime.fromisoformat(row["expires_at"]) < _utcnow():
            return None
        return dict(row)

    def save_sites(
        self,
        *,
        user_id: str,
        project_id: str,
        sites: list[dict],
        access_token: str,
        refresh_token: str | None,
        expires_in: int | None,
    ) -> list[dict]:
        now = _utcnow()
        expires_at = (now + timedelta(seconds=int(expires_in or 3600))).isoformat()
        encrypted_access = self.cipher.encrypt(access_token)
        encrypted_refresh = self.cipher.encrypt(refresh_token)
        with self._connect() as conn:
            cloud_ids = [str(site.get("id", "")) for site in sites if site.get("id")]
            for site in sites:
                conn.execute(
                    """
                    INSERT INTO atlassian_connections(
                        user_id, project_id, cloud_id, site_name, site_url, scopes_json,
                        access_token_encrypted, refresh_token_encrypted, expires_at,
                        status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'connected', ?, ?)
                    ON CONFLICT(user_id, project_id, cloud_id) DO UPDATE SET
                        site_name=excluded.site_name, site_url=excluded.site_url,
                        scopes_json=excluded.scopes_json,
                        access_token_encrypted=excluded.access_token_encrypted,
                        refresh_token_encrypted=CASE
                            WHEN excluded.refresh_token_encrypted != '' THEN excluded.refresh_token_encrypted
                            ELSE atlassian_connections.refresh_token_encrypted END,
                        expires_at=excluded.expires_at, status='connected', updated_at=excluded.updated_at
                    """,
                    (
                        user_id, project_id, str(site.get("id", "")),
                        str(site.get("name", "Atlassian")), str(site.get("url", "")),
                        json.dumps(site.get("scopes", [])), encrypted_access,
                        encrypted_refresh, expires_at, now.isoformat(), now.isoformat(),
                    ),
                )
            if cloud_ids:
                placeholders = ",".join("?" for _ in cloud_ids)
                conn.execute(
                    f"""DELETE FROM atlassian_connections
                        WHERE user_id=? AND project_id=?
                          AND cloud_id NOT IN ({placeholders})""",
                    (user_id, project_id, *cloud_ids),
                )
        return self.list_for_project(project_id, user_id)

    def list_for_project(self, project_id: str, user_id: str) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT id, user_id, project_id, cloud_id, site_name, site_url,
                          scopes_json, expires_at, status, last_sync_at,
                          last_sync_details_json, created_at, updated_at
                   FROM atlassian_connections
                   WHERE project_id = ? AND user_id = ? ORDER BY site_name""",
                (project_id, user_id),
            ).fetchall()
        return [self._decode_public(row) for row in rows]

    def get_with_tokens(self, connection_id: int, user_id: str, project_id: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM atlassian_connections WHERE id=? AND user_id=? AND project_id=?",
                (connection_id, user_id, project_id),
            ).fetchone()
        if not row:
            return None
        data = self._decode_public(row)
        data["access_token"] = self.cipher.decrypt(row["access_token_encrypted"])
        data["refresh_token"] = self.cipher.decrypt(row["refresh_token_encrypted"])
        return data

    def update_tokens(
        self,
        connection_id: int,
        user_id: str,
        project_id: str,
        access_token: str,
        refresh_token: str | None,
        expires_in: int,
    ) -> None:
        now = _utcnow()
        encrypted_refresh = self.cipher.encrypt(refresh_token)
        with self._connect() as conn:
            conn.execute(
                """UPDATE atlassian_connections SET access_token_encrypted=?,
                   refresh_token_encrypted=CASE WHEN ? != '' THEN ? ELSE refresh_token_encrypted END,
                   expires_at=?, status='connected', updated_at=?
                   WHERE user_id=? AND project_id=? AND EXISTS (
                       SELECT 1 FROM atlassian_connections AS selected
                       WHERE selected.id=? AND selected.user_id=? AND selected.project_id=?
                   )""",
                (
                    self.cipher.encrypt(access_token),
                    encrypted_refresh, encrypted_refresh,
                    (now + timedelta(seconds=int(expires_in or 3600))).isoformat(),
                    now.isoformat(), user_id, project_id,
                    connection_id, user_id, project_id,
                ),
            )

    def mark_sync(self, connection_id: int, details: dict, status: str = "connected") -> None:
        now = _utcnow().isoformat()
        with self._connect() as conn:
            conn.execute(
                """UPDATE atlassian_connections SET last_sync_at=?, last_sync_details_json=?,
                   status=?, updated_at=? WHERE id=?""",
                (now, json.dumps(details, ensure_ascii=False, default=str), status, now, connection_id),
            )

    def delete(self, connection_id: int, user_id: str, project_id: str) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "DELETE FROM atlassian_connections WHERE id=? AND user_id=? AND project_id=?",
                (connection_id, user_id, project_id),
            )
        return cur.rowcount > 0

    @staticmethod
    def _decode_public(row) -> dict:
        data = dict(row)
        data["scopes"] = json.loads(data.pop("scopes_json", "[]") or "[]")
        data["last_sync_details"] = json.loads(data.pop("last_sync_details_json", "{}") or "{}")
        data.pop("access_token_encrypted", None)
        data.pop("refresh_token_encrypted", None)
        return data


atlassian_connection_repository = AtlassianConnectionRepository()
