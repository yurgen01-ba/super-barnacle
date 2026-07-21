import unittest

from jobs.knowledge_extraction_service import KnowledgeExtractionJobService
from jobs.running_job import RunningJob


class JobSourceFilterTests(unittest.TestCase):
    def test_meeting_job_is_not_a_jira_job(self):
        job = RunningJob.create("knowledge_extraction", {"source": "meetings"})

        self.assertTrue(KnowledgeExtractionJobService._belongs_to_source(job, "meetings"))
        self.assertFalse(KnowledgeExtractionJobService._belongs_to_source(job, "jira"))

    def test_product_specific_atlassian_job_matches_only_its_section(self):
        job = RunningJob.create(
            "knowledge_extraction", {"source": "atlassian_oauth_confluence"}
        )

        self.assertTrue(KnowledgeExtractionJobService._belongs_to_source(job, "confluence"))
        self.assertFalse(KnowledgeExtractionJobService._belongs_to_source(job, "jira"))

    def test_jira_and_meeting_jobs_are_independently_addressable(self):
        meeting = RunningJob.create(
            "knowledge_extraction", {"source": "meetings", "project_id": "p1"}
        )
        jira = RunningJob.create(
            "knowledge_extraction", {"source": "jira_text", "project_id": "p1"}
        )

        self.assertTrue(KnowledgeExtractionJobService._belongs_to_source(meeting, "meetings"))
        self.assertFalse(KnowledgeExtractionJobService._belongs_to_source(meeting, "jira"))
        self.assertTrue(KnowledgeExtractionJobService._belongs_to_source(jira, "jira"))
        self.assertFalse(KnowledgeExtractionJobService._belongs_to_source(jira, "meetings"))


if __name__ == "__main__":
    unittest.main()
