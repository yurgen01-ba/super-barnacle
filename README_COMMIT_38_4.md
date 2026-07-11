# Commit 38.4 — Streamlit UI Stabilization

## Goal

Improve the existing Streamlit UI without migrating to React/FastAPI yet.

This keeps the project stable while we continue improving Project Intelligence.

## Added

```text
ui/design.py
scripts_replace_streamlit_width.ps1
```

## Replaced

```text
ui/workspace/app_shell.py
ui/workspace/model.py
```

## What changed

### 1. Product-like dark theme

Adds a lightweight Project Brain theme:
- dark background;
- compact tabs;
- rounded cards;
- subtle gradients;
- cleaner Project Model hero.

### 2. Project Model tab layout

Project Model now starts with a compact hero block and shorter tab names:

```text
🚀 Refresh
📌 Summary
🏛️ Domain
👥 Actors
🗺️ Processes
🧬 Ontology
🧠 Knowledge
🧩 Facts
🕸️ Entities
🔗 Relationships
```

### 3. Deprecated Streamlit API helper

Run:

```powershell
.\scripts_replace_streamlit_width.ps1
```

This replaces:

```python
use_container_width=True
```

with:

```python
width="stretch"
```

and:

```python
use_container_width=False
```

with:

```python
width="content"
```

## Apply

Copy:

```text
ui/design.py
ui/workspace/app_shell.py
ui/workspace/model.py
scripts_replace_streamlit_width.ps1
README_COMMIT_38_4.md
```

Then run:

```powershell
.\scripts_replace_streamlit_width.ps1
python -m streamlit run app.py
```

Commit:

```powershell
git add ui/design.py ui/workspace/app_shell.py ui/workspace/model.py scripts_replace_streamlit_width.ps1 README_COMMIT_38_4.md
git add .
git commit -m "Commit 38.4 - Stabilize Streamlit UI"
```
