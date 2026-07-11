# Hotfix for Commit 38.6 — Custom Left Menu

## Problem

Native Streamlit sidebar disappeared/could not be restored after collapse.

## Fix

Replace:

```text
ui_v2/design.py
ui_v2/app_shell.py
ui_v2/layout/sidebar.py
```

## What changed

- UI v2 no longer uses native Streamlit sidebar.
- Left menu is now a regular left column.
- Native sidebar is hidden.
- Menu cannot be accidentally collapsed.

## Run

```powershell
python -m streamlit run app.py
```

## Commit

```powershell
git add ui_v2/design.py ui_v2/app_shell.py ui_v2/layout/sidebar.py README_HOTFIX_38_6_CUSTOM_LEFT_MENU.md
git commit -m "Hotfix UI v2 custom left menu"
```
