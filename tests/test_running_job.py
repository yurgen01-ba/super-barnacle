import re
import unittest

from jobs.running_job import RunningJob


class RunningJobTests(unittest.TestCase):
    def test_progress_log_contains_local_iso_timestamp(self):
        job = RunningJob.create("test")

        job.update_progress(0.5, "processing", "Halfway done")

        self.assertEqual("Halfway done", job.message)
        self.assertRegex(
            job.logs[-1],
            re.compile(
                r"^\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}\] Halfway done$"
            ),
        )


if __name__ == "__main__":
    unittest.main()
