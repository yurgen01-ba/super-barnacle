import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from jobs.running_job import RunningJob
from jobs.job_recovery import resume_incomplete_jobs


class JobRecoveryTests(unittest.TestCase):
    def test_resumes_meeting_job_when_staged_file_exists(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "meeting.mp4"
            source.write_bytes(b"video")
            job = RunningJob.create(
                "knowledge_extraction",
                {
                    "resume_kind": "meeting_videos",
                    "project_id": "project-1",
                    "file_specs": [{"name": "meeting.mp4", "path": str(source)}],
                    "settings": {"language": None},
                },
            )
            job.mark_running()

            with patch("jobs.job_recovery.running_job_store.list", return_value=[job]), patch(
                "jobs.job_recovery.background_job_executor.is_running", return_value=False
            ), patch("jobs.job_recovery.background_job_executor.resume") as resume:
                resumed = resume_incomplete_jobs()

        self.assertEqual([job.id], resumed)
        resume.assert_called_once()


if __name__ == "__main__":
    unittest.main()
