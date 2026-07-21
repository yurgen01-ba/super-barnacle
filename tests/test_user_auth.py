from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from repositories.user_repository import UserRepository
from services.email_notification_service import EmailNotificationService


class UserAuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repository = UserRepository(Path(self.temp_dir.name) / "auth.db")

    def tearDown(self):
        self.temp_dir.cleanup()

    def _register_and_verify(self, email: str, password: str, name: str):
        user = self.repository.register(email=email, password=password, name=name)
        token = user.pop("_verification_token")
        self.assertFalse(user["email_verified"])
        self.assertTrue(self.repository.verify_email(token))
        return self.repository.authenticate(email, password)

    def test_password_policy(self):
        invalid = ["short!1", "Пароль!1A", "Password1", "Password!", "Pass word1!"]
        for password in invalid:
            with self.subTest(password=password), self.assertRaises(ValueError):
                self.repository.validate_password(password)
        self.repository.validate_password("StrongPass1!")

    def test_unverified_user_cannot_login(self):
        self.repository.register("pending@example.com", "StrongPass1!", "Pending")
        with self.assertRaises(ValueError):
            self.repository.authenticate("pending@example.com", "StrongPass1!")

    def test_multiple_users_have_independent_credentials(self):
        alice = self._register_and_verify("alice@example.com", "AlicePass1!", "Alice")
        bob = self._register_and_verify("bob@example.com", "BobSecure2@", "Bob")
        self.assertNotEqual(alice["id"], bob["id"])
        self.assertEqual("alice@example.com", alice["email"])
        self.assertEqual("bob@example.com", bob["email"])
        self.assertIsNone(self.repository.authenticate("alice@example.com", "BobSecure2@"))


class EmailEncodingTests(unittest.TestCase):
    def test_russian_email_is_utf8(self):
        service = EmailNotificationService()
        service.host = "smtp.example.test"
        service.sender = "robot@example.test"
        service.username = ""
        service.use_tls = False
        captured = []

        class FakeSmtp:
            def __init__(self, *args, **kwargs):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def send_message(self, message):
                captured.append(message)

        with patch("services.email_notification_service.smtplib.SMTP", FakeSmtp):
            self.assertTrue(
                service.send(
                    recipient="user@example.test",
                    subject="Подтверждение регистрации",
                    body="Здравствуйте! Обработка завершена.",
                )
            )
        message = captured[0]
        self.assertEqual("utf-8", message.get_content_charset())
        self.assertIn("Здравствуйте", message.get_content())


if __name__ == "__main__":
    unittest.main()
