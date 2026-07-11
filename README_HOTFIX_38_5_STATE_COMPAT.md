# Hotfix for Commit 38.5 — ui_v2.state compatibility aliases

## Problem

```text
ImportError: cannot import name 'get_project' from 'ui_v2.state'
```

## Fix

Replace:

```text
ui_v2/state.py
```

This version supports both naming styles:

```python
get_current_project()
get_project()
get_current_page()
get_page()
```

## Run

```powershell
python -m streamlit run app.py
```

## Commit

```powershell
git add ui_v2/state.py
git commit -m "Hotfix UI v2 state compatibility"
```
