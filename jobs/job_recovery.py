from __future__ import annotations

import threading
from pathlib import Path

from jobs.background_job_executor import background_job_executor
from jobs.extraction_tasks import process_meeting_videos_job
from jobs.running_job_store import running_job_store


_lock = threading.RLock()


def resume_incomplete_jobs() -> list[str]:
    resumed: list[str] = []
    with _lock:
        for job in running_job_store.list(active_only=True):
            if background_job_executor.is_running(job.id):
                continue
            if job.cancel_requested:
                job.mark_cancelled()
                job.add_log("Cancelled job was not resumed after application restart.")
                running_job_store.update(job)
                continue
            metadata = job.metadata or {}
            if metadata.get("resume_kind") != "meeting_videos":
                continue
            file_specs = list(metadata.get("file_specs") or [])
            missing = [spec.get("path") for spec in file_specs if not Path(str(spec.get("path") or "")).is_file()]
            if not file_specs or missing:
                job.mark_failed(
                    "Automatic resume failed because staged source files are missing: "
                    + ", ".join(str(path) for path in missing)
                )
                job.add_log(job.error)
                running_job_store.update(job)
                continue
            background_job_executor.resume(
                job,
                process_meeting_videos_job,
                file_specs=file_specs,
                settings=dict(metadata.get("settings") or {}),
                project_id=str(metadata.get("project_id") or "default"),
            )
            resumed.append(job.id)
    return resumed
