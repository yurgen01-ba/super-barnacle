import unittest
from unittest.mock import patch

from jobs.running_job import RunningJob
from ui_v2.job_activity import _render_active_job_activity


class JobActivityTests(unittest.TestCase):
    def test_renders_all_active_sources_for_current_project(self):
        meeting = RunningJob.create(
            "knowledge_extraction", {"source": "meetings", "project_id": "p1"}
        )
        meeting.progress = 0.42
        jira = RunningJob.create(
            "knowledge_extraction", {"source": "jira_text", "project_id": "p1"}
        )
        jira.progress = 0.18
        other_project = RunningJob.create(
            "knowledge_extraction", {"source": "slack", "project_id": "p2"}
        )
        rendered = []

        with patch(
            "ui_v2.job_activity.running_job_store.list",
            return_value=[meeting, jira, other_project],
        ), patch("ui_v2.job_activity.get_language", return_value="en"), patch(
            "ui_v2.job_activity.favicon_data_uri", return_value="data:image/png;base64,test"
        ), patch(
            "ui_v2.job_activity.st.markdown",
            side_effect=lambda body, **_: rendered.append(body),
        ):
            _render_active_job_activity("p1")

        html = "".join(rendered)
        self.assertIn("Meetings", html)
        self.assertIn("Jira", html)
        self.assertIn("42%", html)
        self.assertIn("18%", html)
        self.assertNotIn("Slack", html)


if __name__ == "__main__":
    unittest.main()
