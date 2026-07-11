# Hotfix for Commit 38.5 — ui_v2.state import

## Problem

```text
ImportError: cannot import name 'get_current_page' from 'ui_v2.state'
```

## Fix

Replace:

```text
ui_v2/state.py
```

## Run

```powershell
python -m streamlit run app.py
```

## Commit

```powershell
git add ui_v2/state.py
git commit -m "Hotfix UI v2 state helpers"
```
