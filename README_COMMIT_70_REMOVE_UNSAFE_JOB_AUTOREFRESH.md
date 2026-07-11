# Commit 70 — Remove Unsafe Job Auto-refresh

## Problem

Commit 69 used:

```python
time.sleep(...)
st.rerun()
```

inside `render_job_status()`.

This can crash Streamlit with:

```text
RuntimeError: Event loop is closed
```

## Fix

Replace unsafe auto-refresh with manual refresh button.

## Changed

```text
ui/job_status.py
```

## Commit

```powershell
git add ui/job_status.py README_COMMIT_70_REMOVE_UNSAFE_JOB_AUTOREFRESH.md
git commit -m "Commit 70 - Remove unsafe job auto-refresh"
```
