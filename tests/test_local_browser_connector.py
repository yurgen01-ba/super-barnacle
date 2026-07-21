from __future__ import annotations

import unittest

from services.local_browser_connector import (
    LocalBrowserConnectorService,
    validate_start_url,
)


class LocalBrowserConnectorTests(unittest.TestCase):
    def test_start_url_requires_http_and_rejects_embedded_credentials(self):
        self.assertEqual(
            validate_start_url("https://company.atlassian.net/jira"),
            "https://company.atlassian.net/jira",
        )
        with self.assertRaises(ValueError):
            validate_start_url("company.atlassian.net")
        with self.assertRaises(ValueError):
            validate_start_url("https://user:secret@company.atlassian.net")

    def test_slack_links_keep_only_same_origin_conversations(self):
        links = LocalBrowserConnectorService.slack_conversation_links(
            [
                {
                    "href": "https://app.slack.com/client/T123/C456",
                    "text": "# product",
                },
                {
                    "href": "https://app.slack.com/client/T123/C456?thread=1",
                    "text": "duplicate",
                },
                {
                    "href": "https://app.slack.com/client/T123/D789",
                    "text": "Alice",
                },
                {
                    "href": "https://evil.example/client/T123/C999",
                    "text": "foreign",
                },
                {"href": "https://app.slack.com/client/T123/threads", "text": "Threads"},
            ],
            "https://app.slack.com",
        )
        self.assertEqual([item["conversation_id"] for item in links], ["C456", "D789"])
        self.assertEqual(links[0]["text"], "product")

    def test_confluence_content_is_converted_to_plain_text(self):
        text = LocalBrowserConnectorService._confluence_browser_text({
            "title": "Architecture",
            "status": "current",
            "space": {"name": "Engineering"},
            "version": {"number": 7},
            "body": {"storage": {"value": "<h1>Decision</h1><p>Use PostgreSQL</p>"}},
        })
        self.assertIn("Architecture", text)
        self.assertIn("Engineering", text)
        self.assertIn("Decision", text)
        self.assertIn("Use PostgreSQL", text)
        self.assertNotIn("<p>", text)


if __name__ == "__main__":
    unittest.main()
