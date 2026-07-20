from __future__ import annotations

import hashlib
import hmac
import os
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PBKDF2_ITERATIONS = 310_000


class UserRepository:
    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path or os.getenv("AUTH_DB_PATH", "data/auth.db"))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    @contextmanager
    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _ensure_schema(self):
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    password_hash BLOB,
                    password_salt BLOB,
                    auth_provider TEXT NOT NULL DEFAULT 'email',
                    provider_subject TEXT,
                    created_at TEXT NOT NULL,
                    last_login_at TEXT
                )
                """
            )
            connection.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_provider_subject "
                "ON users(auth_provider, provider_subject) WHERE provider_subject IS NOT NULL"
            )

    @staticmethod
    def normalize_email(email: str) -> str:
        return str(email or "").strip().lower()

    @staticmethod
    def _hash_password(password: str, salt: bytes) -> bytes:
        return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)

    @staticmethod
    def _public_user(row: sqlite3.Row | dict) -> dict:
        return {
            "id": row["id"],
            "email": row["email"],
            "name": row["name"],
            "auth_provider": row["auth_provider"],
        }

    def register(self, email: str, password: str, name: str = "") -> dict:
        normalized_email = self.normalize_email(email)
        if not EMAIL_RE.match(normalized_email):
            raise ValueError("Введите корректный email.")
        if len(password or "") < 8:
            raise ValueError("Пароль должен содержать не менее 8 символов.")
        clean_name = re.sub(r"\s+", " ", str(name or "").strip()) or normalized_email.split("@", 1)[0]
        salt = os.urandom(16)
        password_hash = self._hash_password(password, salt)
        now = datetime.now(timezone.utc).isoformat()
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO users(
                        id, email, name, password_hash, password_salt,
                        auth_provider, created_at, last_login_at
                    ) VALUES (?, ?, ?, ?, ?, 'email', ?, ?)
                    """,
                    (str(uuid4()), normalized_email, clean_name[:120], password_hash, salt, now, now),
                )
        except sqlite3.IntegrityError as exc:
            raise ValueError("Пользователь с таким email уже зарегистрирован.") from exc
        return self.get_by_email(normalized_email)

    def authenticate(self, email: str, password: str) -> dict | None:
        normalized_email = self.normalize_email(email)
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM users WHERE email = ? AND auth_provider = 'email'",
                (normalized_email,),
            ).fetchone()
            if not row or not row["password_hash"] or not row["password_salt"]:
                return None
            candidate = self._hash_password(password or "", row["password_salt"])
            if not hmac.compare_digest(candidate, row["password_hash"]):
                return None
            connection.execute(
                "UPDATE users SET last_login_at = ? WHERE id = ?",
                (datetime.now(timezone.utc).isoformat(), row["id"]),
            )
        return self._public_user(row)

    def upsert_oidc_user(self, *, email: str, name: str, provider: str, subject: str) -> dict:
        normalized_email = self.normalize_email(email)
        if not EMAIL_RE.match(normalized_email):
            raise ValueError("OIDC-провайдер не вернул корректный email.")
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM users WHERE email = ?", (normalized_email,)).fetchone()
            if row:
                connection.execute(
                    "UPDATE users SET name = ?, last_login_at = ? WHERE id = ?",
                    (name or row["name"], now, row["id"]),
                )
            else:
                connection.execute(
                    """
                    INSERT INTO users(
                        id, email, name, auth_provider, provider_subject, created_at, last_login_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (str(uuid4()), normalized_email, name or normalized_email, provider, subject, now, now),
                )
        return self.get_by_email(normalized_email)

    def get_by_email(self, email: str) -> dict | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM users WHERE email = ?",
                (self.normalize_email(email),),
            ).fetchone()
        return self._public_user(row) if row else None


user_repository = UserRepository()
