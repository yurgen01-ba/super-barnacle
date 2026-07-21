import os
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import httpx

from repositories.atlassian_connection_repository import TokenCipher
from repositories.slack_connection_repository import SlackConnectionRepository
from services.slack_oauth_service import SlackOAuthService


class SlackOAuthTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.db_path = str(root / "project.db")
        self.repo = SlackConnectionRepository(
            db_path=self.db_path,
            cipher=TokenCipher(key_path=str(root / "token.key")),
        )
        self.old_env = dict(os.environ)
        os.environ.update({
            "SLACK_CLIENT_ID": "client-id",
            "SLACK_CLIENT_SECRET": "client-secret",
            "SLACK_REDIRECT_URI": "http://localhost:8501/?slack_callback=1",
        })

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.old_env)
        self.temp.cleanup()

    def test_authorization_url_and_one_time_state(self):
        service = SlackOAuthService(repository=self.repo)
        query = parse_qs(urlparse(service.authorization_url("user-1", "project-1")).query)
        self.assertEqual(query["client_id"], ["client-id"])
        self.assertIn("channels:history", query["user_scope"][0])
        state = query["state"][0]
        self.assertEqual(self.repo.consume_state(state)["project_id"], "project-1")
        self.assertIsNone(self.repo.consume_state(state))

    def test_callback_saves_encrypted_user_token(self):
        def handler(request: httpx.Request):
            return httpx.Response(200, json={
                "ok": True,
                "team": {"id": "team-1", "name": "Demo Slack"},
                "enterprise": None,
                "authed_user": {
                    "id": "slack-user-1",
                    "access_token": "xoxp-secret",
                    "scope": "channels:read,channels:history",
                },
            })

        service = SlackOAuthService(
            repository=self.repo,
            client=httpx.Client(transport=httpx.MockTransport(handler)),
        )
        state = self.repo.create_state("user-1", "project-1")
        result = service.complete_authorization("code-1", state)
        connection = result["connection"]
        self.assertEqual(connection["team_name"], "Demo Slack")
        secret = self.repo.get_with_token(connection["id"], "user-1", "project-1")
        self.assertEqual(secret["access_token"], "xoxp-secret")
        self.assertNotIn(b"xoxp-secret", Path(self.db_path).read_bytes())

    def test_disconnect_revokes_and_deletes_local_token(self):
        calls = []

        def handler(request: httpx.Request):
            calls.append(str(request.url))
            return httpx.Response(200, json={"ok": True})

        connection = self.repo.save(
            user_id="user-1", project_id="project-1", team_id="team-1",
            team_name="Demo", authed_user_id="slack-user-1", scopes=[],
            access_token="xoxp-secret",
        )
        service = SlackOAuthService(
            repository=self.repo,
            client=httpx.Client(transport=httpx.MockTransport(handler)),
        )
        self.assertTrue(service.disconnect(connection["id"], "user-1", "project-1"))
        self.assertTrue(any("auth.revoke" in url for url in calls))
        self.assertEqual(self.repo.list_for_project("project-1", "user-1"), [])


if __name__ == "__main__":
    unittest.main()
