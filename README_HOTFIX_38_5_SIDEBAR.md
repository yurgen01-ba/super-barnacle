# Hotfix for Commit 38.5 — Sidebar button crash

## Problem

Streamlit crashed with:

```text
TypeError: ButtonMixin.button() got an unexpected keyword argument 'label_visibility'
```

`st.button()` does not support `label_visibility`.

## Fix

Replace:

```text
ui_v2/layout/sidebar.py
```

## Run

```powershell
python -m streamlit run app.py
```

## Commit

```powershell
git add ui_v2/layout/sidebar.py
git commit -m "Hotfix UI v2 sidebar button crash"
```
