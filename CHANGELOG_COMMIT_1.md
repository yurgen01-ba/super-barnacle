# Commit 1 — Foundation UI Split + Progress Engine

## Added

- `core/logger.py`
- `core/exceptions.py`
- `config_pkg/settings.py`
- `progress/progress_manager.py`
- `jobs/job.py`
- `jobs/job_manager.py`
- `pipeline/base_pipeline.py`
- `pipeline/pipeline_engine.py`
- `repositories/memory_repository.py`
- `repositories/job_repository.py`
- `ui/common.py`
- `ui/meetings.py`
- `ui/slack.py`
- `ui/jira.py`
- `ui/memory.py`
- `ui/report.py`

## Changed

- `app.py` is now a thin Streamlit shell.
- Report generation now supports `executive` and `analyst` modes.
- Progress is now handled consistently through `ProgressManager`.
- Memory saving is centralized in `MemoryRepository`.

## Preserved

- Meeting video processing.
- Slack paste processing.
- Jira text processing.
- Jira PDF processing.
- SQLite Project Memory.
- Timeline.
- Report generation.

## How to run

```powershell
python -m streamlit run app.py
```
