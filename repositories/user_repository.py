from __future__ import annotations

import hashlib
import hmac
import os
import re
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PBKDF2_ITERATIONS = 310_000
PASSWORD_RE = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9])[\x21-\x7E]{8,}$")


class UserRepositoryError(ValueError):
    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


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
            columns = {
                row[1] for row in connection.execute("PRAGMA table_info(users)").fetchall()
            }
            migrations = {
                "email_verified": "INTEGER NOT NULL DEFAULT 1",
                "verification_token_hash": "TEXT",
                "verification_expires_at": "TEXT",
                "avatar_url": "TEXT",
                "preferred_language": "TEXT",
                "preferred_theme": "TEXT",
            }
            for column, definition in migrations.items():
                if column not in columns:
                    connection.execute(f"ALTER TABLE users ADD COLUMN {column} {definition}")
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
            "email_verified": bool(row["email_verified"]),
            "avatar_url": row["avatar_url"],
            "preferred_language": row["preferred_language"],
            "preferred_theme": row["preferred_theme"],
        }

    @staticmethod
    def validate_password(password: str) -> None:
        if not PASSWORD_RE.fullmatch(password or ""):
            raise UserRepositoryError(
                "password_policy",
                "Пароль должен содержать не менее 8 символов: заглавную и строчную "
                "латинские буквы, цифру и специальный символ. Кириллица и пробелы не допускаются."
            )

    def register(self, email: str, password: str, name: str = "") -> dict:
        normalized_email = self.normalize_email(email)
        if not EMAIL_RE.match(normalized_email):
            raise UserRepositoryError("invalid_email", "Введите корректный email.")
        self.validate_password(password)
        clean_name = re.sub(r"\s+", " ", str(name or "").strip()) or normalized_email.split("@", 1)[0]
        salt = os.urandom(16)
        password_hash = self._hash_password(password, salt)
        now = datetime.now(timezone.utc).isoformat()
        verification_token = secrets.token_urlsafe(32)
        verification_hash = hashlib.sha256(verification_token.encode("utf-8")).hexdigest()
        verification_expires_at = datetime.fromtimestamp(
            datetime.now(timezone.utc).timestamp() + 24 * 60 * 60,
            tz=timezone.utc,
        ).isoformat()
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO users(
                        id, email, name, password_hash, password_salt,
                        auth_provider, email_verified, verification_token_hash,
                        verification_expires_at, created_at, last_login_at
                    ) VALUES (?, ?, ?, ?, ?, 'email', 0, ?, ?, ?, NULL)
                    """,
                    (
                        str(uuid4()), normalized_email, clean_name[:120], password_hash, salt,
                        verification_hash, verification_expires_at, now,
                    ),
                )
        except sqlite3.IntegrityError as exc:
            raise UserRepositoryError("duplicate_email", "Пользователь с таким email уже зарегистрирован.") from exc
        user = self.get_by_email(normalized_email)
        user["_verification_token"] = verification_token
        return user

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
            if not bool(row["email_verified"]):
                raise UserRepositoryError("email_not_verified", "Подтвердите email по ссылке из письма перед входом.")
            connection.execute(
                "UPDATE users SET last_login_at = ? WHERE id = ?",
                (datetime.now(timezone.utc).isoformat(), row["id"]),
            )
        return self._public_user(row)

    def upsert_oidc_user(
        self,
        *,
        email: str,
        name: str,
        provider: str,
        subject: str,
        avatar_url: str | None = None,
    ) -> dict:
        normalized_email = self.normalize_email(email)
        if not EMAIL_RE.match(normalized_email):
            raise UserRepositoryError("invalid_oidc_email", "OIDC-провайдер не вернул корректный email.")
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM users WHERE email = ?", (normalized_email,)).fetchone()
            if row:
                connection.execute(
                    """
                    UPDATE users SET name = ?, avatar_url = COALESCE(?, avatar_url),
                        email_verified = 1, last_login_at = ? WHERE id = ?
                    """,
                    (name or row["name"], avatar_url, now, row["id"]),
                )
            else:
                connection.execute(
                    """
                    INSERT INTO users(
                        id, email, name, auth_provider, provider_subject,
                        email_verified, avatar_url, created_at, last_login_at
                    ) VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?)
                    """,
                    (
                        str(uuid4()), normalized_email, name or normalized_email, provider,
                        subject, avatar_url, now, now,
                    ),
                )
        return self.get_by_email(normalized_email)

    def verify_email(self, token: str) -> bool:
        token_hash = hashlib.sha256(str(token or "").encode("utf-8")).hexdigest()
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id FROM users
                WHERE verification_token_hash = ?
                  AND verification_expires_at IS NOT NULL
                  AND verification_expires_at >= ?
                """,
                (token_hash, now),
            ).fetchone()
            if not row:
                return False
            connection.execute(
                """
                UPDATE users SET email_verified = 1, verification_token_hash = NULL,
                    verification_expires_at = NULL WHERE id = ?
                """,
                (row["id"],),
            )
        return True

    def create_verification_token(self, email: str) -> str | None:
        user = self.get_by_email(email)
        if not user or user["email_verified"]:
            return None
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        expires = datetime.fromtimestamp(
            datetime.now(timezone.utc).timestamp() + 24 * 60 * 60,
            tz=timezone.utc,
        ).isoformat()
        with self._connect() as connection:
            connection.execute(
                "UPDATE users SET verification_token_hash = ?, verification_expires_at = ? WHERE email = ?",
                (token_hash, expires, self.normalize_email(email)),
            )
        return token

    def update_profile(self, user_id: str, *, name: str, avatar_url: str | None = None) -> dict:
        clean_name = re.sub(r"\s+", " ", str(name or "").strip())
        if not clean_name:
            raise UserRepositoryError("name_required", "Имя не может быть пустым.")
        with self._connect() as connection:
            connection.execute(
                "UPDATE users SET name = ?, avatar_url = COALESCE(?, avatar_url) WHERE id = ?",
                (clean_name[:120], avatar_url, user_id),
            )
        return self.get_by_id(user_id)

    def update_preferences(
        self,
        user_id: str,
        *,
        language: str | None = None,
        theme: str | None = None,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE users SET preferred_language = COALESCE(?, preferred_language),
                    preferred_theme = COALESCE(?, preferred_theme) WHERE id = ?
                """,
                (language, theme, user_id),
            )

    def change_password(self, user_id: str, current_password: str, new_password: str) -> None:
        self.validate_password(new_password)
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            if not row or row["auth_provider"] != "email":
                raise UserRepositoryError("oauth_password", "Пароль управляется внешним провайдером авторизации.")
            candidate = self._hash_password(current_password or "", row["password_salt"])
            if not hmac.compare_digest(candidate, row["password_hash"]):
                raise UserRepositoryError("current_password_wrong", "Текущий пароль указан неверно.")
            salt = os.urandom(16)
            password_hash = self._hash_password(new_password, salt)
            connection.execute(
                "UPDATE users SET password_hash = ?, password_salt = ? WHERE id = ?",
                (password_hash, salt, user_id),
            )

    def get_by_id(self, user_id: str) -> dict | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return self._public_user(row) if row else None

    def get_by_email(self, email: str) -> dict | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM users WHERE email = ?",
                (self.normalize_email(email),),
            ).fetchone()
        return self._public_user(row) if row else None


user_repository = UserRepository()
