from jobs.job_manager import JobManager


class JobRepository:
    def __init__(self):
        self.job_manager = JobManager()

    def create(self, name: str, source: str):
        return self.job_manager.create_job(name=name, source=source)

    def list_all(self):
        return self.job_manager.list_jobs()

