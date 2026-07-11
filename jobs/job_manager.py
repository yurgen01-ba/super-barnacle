from jobs.job import Job


class JobManager:
    def __init__(self):
        self.jobs: dict[str, Job] = {}

    def create_job(self, name: str, source: str) -> Job:
        job = Job(name=name, source=source)
        self.jobs[job.id] = job
        return job

    def get_job(self, job_id: str) -> Job | None:
        return self.jobs.get(job_id)

    def list_jobs(self) -> list[Job]:
        return list(self.jobs.values())

