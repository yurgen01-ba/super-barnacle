# Commit 69 — Live Progress Reporting

## Goal

Make background knowledge extraction visibly progress while the user stays on or returns to the page.

## Problem

The job was running, but progress stayed at 0% because meeting extractor callbacks were not connected to `RunningJob`.

## Changed

```text
jobs/extraction_tasks.py
ui/job_status.py
```

## What changed

- Meeting extraction now passes live callbacks into `process_meeting_video`.
- Audio transcription, vision analysis, fact extraction and knowledge extraction update `RunningJob.progress`.
- Text sources now explicitly mark completion.
- Job status UI auto-refreshes while a job is running.

## Commit

```powershell
git add jobs/extraction_tasks.py ui/job_status.py README_COMMIT_69_LIVE_PROGRESS_REPORTING.md
git commit -m "Commit 69 - Add live progress reporting for extraction jobs"
```
