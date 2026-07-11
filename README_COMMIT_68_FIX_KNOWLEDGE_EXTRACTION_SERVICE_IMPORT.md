# Commit 68 — Fix Knowledge Extraction Service Import

## Problem

Previous Commit 68 archive accidentally contained patch snippets instead of full Python files.
That broke imports:

```text
ImportError: cannot import name 'KnowledgeExtractionJobService'
```

## Fix

Replace full files:

```text
jobs/background_job_executor.py
jobs/knowledge_extraction_service.py
```

## What changed

- Restores `KnowledgeExtractionJobService`.
- Removes `run_with_progress`.
- Passes `job` directly from `BackgroundJobExecutor` to extraction callables.
- Fixes `run_with_progress() got multiple values for argument 'job'`.

## Commit

```powershell
git add jobs/background_job_executor.py jobs/knowledge_extraction_service.py README_COMMIT_68_FIX_KNOWLEDGE_EXTRACTION_SERVICE_IMPORT.md
git commit -m "Commit 68 - Fix Knowledge Extraction Service import"
```
