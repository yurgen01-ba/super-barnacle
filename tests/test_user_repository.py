import tempfile
import unittest
from pathlib import Path

from repositories.user_repository import UserRepository


class UserRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repository = UserRepository(Path(self.temp_dir.name) / "auth.db")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_registers_verifies_and_authenticates_email_user(self):
        user = self.repository.register("User@Example.com", "Secure1!", "Test User")
        self.assertEqual(user["email"], "user@example.com")
        self.assertTrue(self.repository.verify_email(user["_verification_token"]))
        authenticated = self.repository.authenticate("user@example.com", "Secure1!")
        self.assertEqual(authenticated["id"], user["id"])

    def test_rejects_wrong_password(self):
        self.repository.register("user@example.com", "Secure1!")
        self.assertIsNone(self.repository.authenticate("user@example.com", "Wrong2!"))

    def test_rejects_duplicate_email(self):
        self.repository.register("user@example.com", "Secure1!")
        with self.assertRaisesRegex(ValueError, "уже зарегистрирован"):
            self.repository.register("USER@example.com", "Another2!")

    def test_requires_valid_email_and_password_policy(self):
        with self.assertRaisesRegex(ValueError, "корректный email"):
            self.repository.register("not-an-email", "Secure1!")
        with self.assertRaisesRegex(ValueError, "не менее 8"):
            self.repository.register("user@example.com", "short")


if __name__ == "__main__":
    unittest.main()
