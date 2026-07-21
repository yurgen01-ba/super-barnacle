import sqlite3
import tempfile
import unittest
from pathlib import Path

from repositories.workspace_repository import WorkspaceRepository


class WorkspaceIsolationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "workspace.db"

        def connect():
            connection = sqlite3.connect(self.db_path)
            connection.row_factory = sqlite3.Row
            return connection

        self.repository = WorkspaceRepository(connection_factory=connect)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_users_receive_distinct_private_projects(self):
        first = self.repository.ensure_user_workspace("user-a", "a@example.com", "A")
        second = self.repository.ensure_user_workspace("user-b", "b@example.com", "B")

        self.assertNotEqual(first["id"], second["id"])
        self.assertEqual([first["id"]], [p["id"] for p in self.repository.list_projects("user-a")])
        self.assertEqual([second["id"]], [p["id"] for p in self.repository.list_projects("user-b")])
        self.assertIsNone(self.repository.get_project(first["id"], "user-b"))

    def test_cross_user_project_mutation_is_rejected(self):
        first = self.repository.ensure_user_workspace("user-a", "a@example.com", "A")
        self.repository.ensure_user_workspace("user-b", "b@example.com", "B")

        with self.assertRaises(PermissionError):
            self.repository.rename_project(first["id"], "Stolen", "user-b")

        self.assertEqual("OrgMeter", self.repository.get_project(first["id"], "user-a")["name"])

    def test_owner_can_share_block_restore_and_remove_access(self):
        project = self.repository.ensure_user_workspace("owner", "owner@example.com", "Owner")
        self.repository.ensure_user_workspace("member", "member@example.com", "Member")
        membership = self.repository.add_member(
            project["id"], "owner", email="member@example.com", user_id="member", name="Member"
        )
        self.assertIsNotNone(self.repository.get_project(project["id"], "member"))

        self.repository.set_member_status(project["id"], "owner", membership["id"], "blocked")
        self.assertIsNone(self.repository.get_project(project["id"], "member"))

        self.repository.set_member_status(project["id"], "owner", membership["id"], "active")
        self.assertIsNotNone(self.repository.get_project(project["id"], "member"))

        self.repository.remove_member(project["id"], "owner", membership["id"])
        self.assertIsNone(self.repository.get_project(project["id"], "member"))

    def test_pending_email_membership_binds_on_first_login(self):
        project = self.repository.ensure_user_workspace("owner", "owner@example.com", "Owner")
        self.repository.add_member(project["id"], "owner", email="future@example.com")

        bound = self.repository.ensure_user_workspace("future-user", "future@example.com", "Future")
        self.assertEqual(project["id"], bound["id"])
        self.assertIsNotNone(self.repository.get_project(project["id"], "future-user"))


if __name__ == "__main__":
    unittest.main()
