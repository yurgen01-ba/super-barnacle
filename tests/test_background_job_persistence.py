import sqlite3
import tempfile
import unittest
from pathlib import Path

from jobs.running_job import RunningJob
from repositories.background_job_repository import BackgroundJobRepository


class BackgroundJobPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temporary_directory.name) / "jobs.db"

        def connect():
            connection = sqlite3.connect(self.database_path)
            connection.row_factory = sqlite3.Row
            return connection

        self.repository = BackgroundJobRepository(connect)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_job_round_trip_preserves_resume_metadata_and_logs(self):
        job = RunningJob.create(
            "knowledge_extraction",
            {
                "resume_kind": "meeting_videos",
                "file_specs": [{"name": "meeting.mp4", "path": "durable/meeting.mp4"}],
                "settings": {"language": None},
            },
        )
        job.mark_running()
        job.update_progress(0.4, "meeting:transcription", "Segment 2/5")
        self.repository.save(job)

        restored = self.repository.get(job.id)

        self.assertEqual(job.id, restored.id)
        self.assertEqual("running", restored.status)
        self.assertEqual("meeting_videos", restored.metadata["resume_kind"])
        self.assertEqual("Segment 2/5", restored.message)
        self.assertIn("Segment 2/5", restored.logs[-1])


if __name__ == "__main__":
    unittest.main()
