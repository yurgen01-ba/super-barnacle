# Hotfix for Commit 38.5 — Clean Dashboard Layout

## Problem

The previous stable-layout hotfix still produced poor UX:
- huge empty right panel;
- sidebar too small;
- old meeting processor exposed directly on Dashboard;
- dashboard looked like old Streamlit forms inside new UI.

## Fix

Replace:

```text
ui_v2/design.py
ui_v2/app_shell.py
ui_v2/layout/sidebar.py
ui_v2/layout/topbar.py
ui_v2/pages/dashboard.py
```

## What changed

- Removed permanent right AI panel.
- AI Chat is now always available via compact topbar popover.
- Removed 3-column app shell.
- Uses native Streamlit sidebar for stable layout.
- Dashboard data loading now starts with clean source cards.
- Full old processors are hidden inside Advanced tabs/expanders.
- Project Model remains hidden in Project menu → Модель проекта · Beta.

## Run

```powershell
python -m streamlit run app.py
```

## Commit

```powershell
git add ui_v2/design.py ui_v2/app_shell.py ui_v2/layout/sidebar.py ui_v2/layout/topbar.py ui_v2/pages/dashboard.py README_HOTFIX_38_5_CLEAN_DASHBOARD.md
git commit -m "Hotfix UI v2 clean dashboard layout"
```
