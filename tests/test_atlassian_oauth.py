import os
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import httpx

from repositories.atlassian_connection_repository import (
    AtlassianConnectionRepository,
    TokenCipher,
)
from services.atlassian_oauth_service import AtlassianOAuthService
from services.atlassian_sync_service import AtlassianSyncService, _adf_text, _html_text


class AtlassianOAuthTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.db_path = str(root / "project.db")
        self.repo = AtlassianConnectionRepository(
            db_path=self.db_path,
            cipher=TokenCipher(key_path=str(root / "token.key")),
        )
        self.old_env = dict(os.environ)
        os.environ.update({
            "ATLASSIAN_CLIENT_ID": "client-id",
            "ATLASSIAN_CLIENT_SECRET": "client-secret",
            "ATLASSIAN_REDIRECT_URI": "http://localhost:8501/?atlassian_callback=1",
        })

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.old_env)
        self.temp.cleanup()

    def test_authorization_url_and_one_time_state(self):
        service = AtlassianOAuthService(repository=self.repo)
        url = service.authorization_url("user-1", "project-1")
        query = parse_qs(urlparse(url).query)
        self.assertEqual(query["client_id"], ["client-id"])
        self.assertIn("offline_access", query["scope"][0])
        self.assertIn("read:attachment:confluence", query["scope"][0])
        state = query["state"][0]
        self.assertEqual(self.repo.consume_state(state)["project_id"], "project-1")
        self.assertIsNone(self.repo.consume_state(state))

    def test_product_authorization_urls_request_only_relevant_scopes(self):
        service = AtlassianOAuthService(repository=self.repo)

        jira_query = parse_qs(urlparse(
            service.authorization_url("user-1", "project-1", product="jira")
        ).query)
        jira_scopes = jira_query["scope"][0]
        self.assertIn("read:jira-work", jira_scopes)
        self.assertIn("read:me", jira_scopes)
        self.assertNotIn("confluence", jira_scopes)

        confluence_query = parse_qs(urlparse(
            service.authorization_url("user-1", "project-1", product="confluence")
        ).query)
        confluence_scopes = confluence_query["scope"][0]
        self.assertIn("read:confluence-content.all", confluence_scopes)
        self.assertIn("read:me", confluence_scopes)
        self.assertNotIn("jira", confluence_scopes)

    def test_callback_saves_encrypted_tokens(self):
        def handler(request: httpx.Request):
            if request.url.path == "/oauth/token":
                return httpx.Response(200, json={
                    "access_token": "access-secret", "refresh_token": "refresh-secret",
                    "expires_in": 3600,
                })
            return httpx.Response(200, json=[{
                "id": "cloud-1", "name": "Demo", "url": "https://demo.atlassian.net",
                "scopes": ["read:jira-work", "read:confluence-content.all"],
            }])

        client = httpx.Client(transport=httpx.MockTransport(handler))
        service = AtlassianOAuthService(repository=self.repo, client=client)
        state = self.repo.create_state("user-1", "project-1")
        service.complete_authorization("code-1", state)
        public = self.repo.list_for_project("project-1", "user-1")
        self.assertEqual(public[0]["site_name"], "Demo")
        self.assertNotIn("access_token", public[0])
        secret = self.repo.get_with_tokens(public[0]["id"], "user-1", "project-1")
        self.assertEqual(secret["access_token"], "access-secret")
        self.assertEqual(secret["refresh_token"], "refresh-secret")
        raw = Path(self.db_path).read_bytes()
        self.assertNotIn(b"access-secret", raw)
        self.assertNotIn(b"refresh-secret", raw)

    def test_content_normalization(self):
        self.assertEqual(_adf_text({
            "type": "doc", "content": [{"type": "paragraph", "content": [
                {"type": "text", "text": "Hello"}
            ]}],
        }).strip(), "Hello")
        self.assertEqual(_html_text("<p>Hello <strong>world</strong></p>"), "Hello\nworld")

    def test_confluence_cursor_keeps_oauth_cloud_path(self):
        base = "https://api.atlassian.com/ex/confluence/cloud-1"
        self.assertEqual(
            AtlassianSyncService._confluence_next_url(
                base, "/wiki/api/v2/pages?cursor=next"
            ),
            base + "/wiki/api/v2/pages?cursor=next",
        )

    def test_rotating_refresh_token_is_propagated_to_all_sites(self):
        sites = [
            {"id": "cloud-1", "name": "One", "url": "https://one.atlassian.net"},
            {"id": "cloud-2", "name": "Two", "url": "https://two.atlassian.net"},
        ]
        connections = self.repo.save_sites(
            user_id="user-1", project_id="project-1", sites=sites,
            access_token="old-access", refresh_token="old-refresh", expires_in=1,
        )
        self.repo.update_tokens(
            connections[0]["id"], "user-1", "project-1",
            "new-access", "new-refresh", 3600,
        )
        for connection in self.repo.list_for_project("project-1", "user-1"):
            secret = self.repo.get_with_tokens(connection["id"], "user-1", "project-1")
            self.assertEqual(secret["access_token"], "new-access")
            self.assertEqual(secret["refresh_token"], "new-refresh")


if __name__ == "__main__":
    unittest.main()
