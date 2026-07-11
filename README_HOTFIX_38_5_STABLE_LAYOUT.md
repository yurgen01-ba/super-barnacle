# Hotfix for Commit 38.5 — Stable Streamlit Layout

## Problem

UI v2 layout collapsed because custom HTML wrappers were mixed with Streamlit widgets.

Streamlit does not guarantee that widgets stay inside raw HTML `<div>` wrappers.

## Fix

Replace:

```text
ui_v2/design.py
ui_v2/app_shell.py
ui_v2/layout/sidebar.py
ui_v2/layout/topbar.py
ui_v2/layout/assistant.py
ui_v2/pages/dashboard.py
```

## What changed

- Removed fragile raw HTML grid layout.
- Replaced it with stable `st.columns`.
- Kept dark visual style.
- Kept:
  - Dashboard-first workflow;
  - upload from Dashboard;
  - AI Assistant always visible on the right;
  - Project Model hidden under Project menu;
  - no Quick Actions;
  - no AI Suggestions.

## Run

```powershell
python -m streamlit run app.py
```

## Commit

```powershell
git add ui_v2/design.py ui_v2/app_shell.py ui_v2/layout/sidebar.py ui_v2/layout/topbar.py ui_v2/layout/assistant.py ui_v2/pages/dashboard.py README_HOTFIX_38_5_STABLE_LAYOUT.md
git commit -m "Hotfix UI v2 stable Streamlit layout"
```
