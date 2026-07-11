# Commit 38.5 — UI v2 Dashboard Workspace

## Goal

Implement the approved dashboard/workspace direction without migrating away from Streamlit yet.

## Added

```text
ui_v2/
  app_shell.py
  design.py
  state.py
  layout/sidebar.py
  layout/topbar.py
  layout/assistant.py
  components/html.py
  pages/dashboard.py
  pages/sources.py
  pages/project_model.py
  pages/settings.py
```

## Replaced

```text
app.py
```

## Implemented UX decisions

- Multi-project foundation: current project selector and Add Project button.
- Dashboard-first workflow.
- Data upload directly from Dashboard.
- AI Assistant always available on the right.
- Sources as nested menu.
- Hidden geek Project Model under Project menu → Модель проекта · Beta.
- Removed Quick Actions, AI Suggestions, separate Artifacts menu, separate AI Analyst menu.

## Run

```powershell
python -m streamlit run app.py
```

## Switch back to old UI

```powershell
$env:PROJECT_BRAIN_UI="old"
python -m streamlit run app.py
```

## Commit

```powershell
git add app.py ui_v2 README_COMMIT_38_5.md
git commit -m "Commit 38.5 - Add UI v2 dashboard workspace"
```
