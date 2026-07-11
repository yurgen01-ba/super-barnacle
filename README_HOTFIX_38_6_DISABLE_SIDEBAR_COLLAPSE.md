# Hotfix for Commit 38.6 — Disable Sidebar Collapse

## Problem

The native Streamlit sidebar could be collapsed, but in this UI v2 build it could not be reliably restored from the custom layout.

## Fix

Replace:

```text
ui_v2/design.py
ui_v2/app_shell.py
```

## What changed

- Forces sidebar to start expanded.
- Hides native Streamlit collapse control.
- Keeps sidebar width fixed at 280px.

## Run

```powershell
python -m streamlit run app.py
```

## Commit

```powershell
git add ui_v2/design.py ui_v2/app_shell.py README_HOTFIX_38_6_DISABLE_SIDEBAR_COLLAPSE.md
git commit -m "Hotfix UI v2 disable sidebar collapse"
```
