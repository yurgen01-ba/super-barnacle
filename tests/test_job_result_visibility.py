from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from ui_v2 import state


class JobResultVisibilityTests(unittest.TestCase):
    def test_terminal_source_job_is_dismissed_by_exact_id(self):
        session_state = {}
        job = Mock(id="completed-job")
        job.is_active.return_value = False

        with (
            patch.object(state, "st", SimpleNamespace(session_state=session_state)),
            patch(
                "jobs.knowledge_extraction_service.KnowledgeExtractionJobService.latest",
                return_value=job,
            ) as latest,
        ):
            state.dismiss_latest_source_job_result("project-1", "jira")

            self.assertTrue(state.is_job_result_dismissed("completed-job"))
            self.assertFalse(state.is_job_result_dismissed("new-job"))
            latest.assert_called_once_with(
                active_only=False,
                project_id="project-1",
                source_section="jira",
            )

    def test_active_source_job_is_never_dismissed(self):
        session_state = {}
        job = Mock(id="running-job")
        job.is_active.return_value = True

        with (
            patch.object(state, "st", SimpleNamespace(session_state=session_state)),
            patch(
                "jobs.knowledge_extraction_service.KnowledgeExtractionJobService.latest",
                return_value=job,
            ),
        ):
            state.dismiss_latest_source_job_result("project-1", "meetings")

            self.assertFalse(state.is_job_result_dismissed("running-job"))


if __name__ == "__main__":
    unittest.main()
