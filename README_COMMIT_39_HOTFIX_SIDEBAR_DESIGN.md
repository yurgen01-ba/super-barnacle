# Commit 39 Hotfix — Sidebar Design

## Problem

After Commit 39:
- `Sources menu` header was white due to native Streamlit expander styling.
- `Project menu` did not match the design.
- Current project card looked too verbose and inconsistent.

## Fix

Replace:

```text
ui_v2/design.py
ui_v2/layout/menu.py
```

## What changed

- Removed native expander for Sources menu.
- Removed native expander for Project menu.
- Replaced them with stable custom dark menu blocks.
- Current project card is now compact and closer to the approved design.

## Run

```powershell
python -m streamlit run app.py
```

## Commit

```powershell
git add ui_v2/design.py ui_v2/layout/menu.py README_COMMIT_39_HOTFIX_SIDEBAR_DESIGN.md
git commit -m "Hotfix UI v2 sidebar design"
```
