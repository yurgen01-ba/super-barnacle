# Commit 71 — Safe Live Job Status

## Goal

Remove manual `Refresh status` button and keep status updates safe.

## Changed

```text
ui/job_status.py
```

## What changed

- Removed `Refresh status` button.
- Removed unsafe `time.sleep() + st.rerun()`.
- Added safe `st.fragment(run_every="2s")` when available.
- Keeps `Cancel job`.
- Status updates automatically without breaking Streamlit event loop.

## Commit

```powershell
git add ui/job_status.py README_COMMIT_71_SAFE_LIVE_JOB_STATUS.md
git commit -m "Commit 71 - Add safe live job status"
```
